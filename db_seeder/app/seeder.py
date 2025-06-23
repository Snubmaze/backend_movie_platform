import asyncio
import os
from passlib.context import CryptContext
from sqlalchemy import text
from database import new_session
from data import users, films, reviews


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def seed():
    async with new_session() as session:
        # 1) Очистка всех таблиц
        try:
            await session.execute(text("""
                TRUNCATE TABLE
                  movie_actors,
                  movie_directors,
                  movie_countries,
                  movie_genres,
                  movies,
                  actors,
                  directors,
                  countries,
                  users,
                  reviews,
                  subscription_plans, 
                  subscriptions,
                  payments                  
                RESTART IDENTITY CASCADE
            """))
            await session.commit()
        except Exception as e:
            await session.rollback()
            print("Cleanup error:", e)

        # 2) Справочники: genres, countries, directors, actors
        try:
            # Genres
            for name in {g for film in films for g in film["genres"]}:
                await session.execute(
                    text("INSERT INTO genres(name) VALUES (:name) ON CONFLICT DO NOTHING"),
                    {"name": name}
                )
            # Countries
            for name in {c for film in films for c in film["countries"]}:
                await session.execute(
                    text("INSERT INTO countries(name) VALUES (:name) ON CONFLICT DO NOTHING"),
                    {"name": name}
                )
            # Directors
            for name in {d for film in films for d in film["directors"]}:
                await session.execute(
                    text("INSERT INTO directors(full_name) VALUES (:name) ON CONFLICT DO NOTHING"),
                    {"name": name}
                )
            #тарифы подписок
            for name, price, days in [
                ('1 month', 199.00,  30),
                ('3 months',349.00,  90),
                ('1 year',  499.00, 365),
            ]:
                await session.execute(
                    text("""
                        INSERT INTO subscription_plans (name, price, period_days)
                        VALUES (:name, :price, :days)
                        ON CONFLICT (name) DO NOTHING
                    """),
                    {"name": name, "price": price, "days": days}
                )
            # Actors
            for name in {a for film in films for a in film["actors"]}:
                await session.execute(
                    text("INSERT INTO actors(full_name) VALUES (:name) ON CONFLICT DO NOTHING"),
                    {"name": name}
                )
            await session.commit()
        except Exception as e:
            await session.rollback()
            print("Seeding lookup tables error:", e)

        # 3) Пользователи
        try:
            for u in users:
                pw_hash = hash_password(u["password"])
                if u["username"] == "snubmaze":
                    # для snubmaze ставим роль admin
                    await session.execute(
                        text("""
                            INSERT INTO users(username, password_hash, role)
                            VALUES(:username, :pw, 'admin')
                            ON CONFLICT (username) DO NOTHING
                        """),
                        {"username": u["username"], "pw": pw_hash}
                    )
                else:
                    await session.execute(
                        text("""
                            INSERT INTO users(username, password_hash)
                            VALUES(:username, :pw)
                            ON CONFLICT (username) DO NOTHING
                        """),
                        {"username": u["username"], "pw": pw_hash}
                    )
            await session.commit()
        except Exception as e:
            await session.rollback()
            print("Seeding users error:", e)

        # 4) Фильмы и связи
        for film in films:
            try:
                # Вставка или получение movie_id
                movie_id = await session.scalar(
                    text("SELECT movie_id FROM movies WHERE title = :title"),
                    {"title": film["title"]}
                )
                if not movie_id:
                    result = await session.execute(
                        text("""
                            INSERT INTO movies
                              (title, description, release_year, duration_min, avg_rating, poster_url, trailer_url)
                            VALUES
                              (:title, :description, :release_year, :duration_min, :avg_rating, :poster_url, :trailer_url)
                            RETURNING movie_id
                        """), film
                    )
                    movie_id = result.scalar_one()

                # M2M связи
                for name in film["genres"]:
                    gid = await session.scalar(
                        text("SELECT genre_id FROM genres WHERE name = :name"),
                        {"name": name}
                    )
                    await session.execute(
                        text("""
                            INSERT INTO movie_genres(movie_id, genre_id)
                            VALUES(:mid, :gid)
                            ON CONFLICT DO NOTHING
                        """), {"mid": movie_id, "gid": gid}
                    )
                for name in film["countries"]:
                    cid = await session.scalar(
                        text("SELECT country_id FROM countries WHERE name = :name"),
                        {"name": name}
                    )
                    await session.execute(
                        text("""
                            INSERT INTO movie_countries(movie_id, country_id)
                            VALUES(:mid, :cid)
                            ON CONFLICT DO NOTHING
                        """), {"mid": movie_id, "cid": cid}
                    )
                for name in film["directors"]:
                    did = await session.scalar(
                        text("SELECT director_id FROM directors WHERE full_name = :name"),
                        {"name": name}
                    )
                    await session.execute(
                        text("""
                            INSERT INTO movie_directors(movie_id, director_id)
                            VALUES(:mid, :did)
                            ON CONFLICT DO NOTHING
                        """), {"mid": movie_id, "did": did}
                    )
                for name in film["actors"]:
                    aid = await session.scalar(
                        text("SELECT actor_id FROM actors WHERE full_name = :name"),
                        {"name": name}
                    )
                    await session.execute(
                        text("""
                            INSERT INTO movie_actors(movie_id, actor_id)
                            VALUES(:mid, :aid)
                            ON CONFLICT DO NOTHING
                        """), {"mid": movie_id, "aid": aid}
                    )
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"Seeding film '{film['title']}' error:", e)

        # 5) Отзывы и рейтинги
        for rev in reviews:
            try:
                user_id  = await session.scalar(
                    text("SELECT user_id FROM users WHERE username = :u"),
                    {"u": rev["username"]}
                )
                movie_id = await session.scalar(
                    text("SELECT movie_id FROM movies WHERE title = :t"),
                    {"t": rev["title"]}
                )
                await session.execute(
                    text("""
                        INSERT INTO reviews(user_id, movie_id, rating, review_text)
                        VALUES(:uid, :mid, :rating, :text)
                        ON CONFLICT (user_id, movie_id) DO UPDATE
                          SET rating      = EXCLUDED.rating,
                              review_text = EXCLUDED.review_text,
                              updated_at  = CURRENT_TIMESTAMP
                    """),
                    {
                        "uid":    user_id,
                        "mid":    movie_id,
                        "rating": rev["rating"],
                        "text":   rev["review_text"]
                    }
                )
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"Seeding review for user '{rev['username']}', movie '{rev['title']}' error:", e)

if __name__ == "__main__":
    asyncio.run(seed())

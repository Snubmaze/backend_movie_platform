#!/usr/bin/env python3
import asyncio
import os
import hashlib
from sqlalchemy import text
from database import new_session

def hash_password(password: str) -> str:
    """
    Генерирует соль и хэш пароля через PBKDF2-HMAC-SHA256.
    Возвращает строку 'salt:hash' в hex.
    """
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return f"{salt.hex()}:{dk.hex()}"

films = [
    {
        "title": "Inception",
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea.",
        "release_year": 2010,
        "duration_min": 148,
        "avg_rating": 8.8,
        "poster_url": None,
        "trailer_url": None,
        "genres": ["Action", "Sci-Fi", "Thriller"],
        "countries": ["USA", "UK"],
        "directors": ["Christopher Nolan"],
        "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"],
    },
    {
        "title": "The Godfather",
        "description": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
        "release_year": 1972,
        "duration_min": 175,
        "avg_rating": 9.2,
        "poster_url": None,
        "trailer_url": None,
        "genres": ["Crime", "Drama"],
        "countries": ["USA"],
        "directors": ["Francis Ford Coppola"],
        "actors": ["Marlon Brando", "Al Pacino"],
    },
    {
        "title": "Spirited Away",
        "description": "During her family's move to the suburbs, a sullen 10-year-old wanders into a world ruled by gods and spirits.",
        "release_year": 2001,
        "duration_min": 125,
        "avg_rating": 8.6,
        "poster_url": None,
        "trailer_url": None,
        "genres": ["Animation", "Adventure", "Family"],
        "countries": ["Japan"],
        "directors": ["Hayao Miyazaki"],
        "actors": ["Rumi Hiiragi", "Miyu Irino"],
    },
    {
        "title": "Parasite",
        "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
        "release_year": 2019,
        "duration_min": 132,
        "avg_rating": 8.6,
        "poster_url": None,
        "trailer_url": None,
        "genres": ["Comedy", "Drama", "Thriller"],
        "countries": ["South Korea"],
        "directors": ["Bong Joon Ho"],
        "actors": ["Song Kang-ho", "Lee Sun-kyun"],
    },
]

users = [
    {"username": "alice", "password": "password"},
    {"username": "bob",   "password": "password"},
]

reviews = [
    {"username": "alice", "title": "Inception",     "rating":  9, "review_text": "Amazing visuals and story."},
    {"username": "bob",   "title": "Inception",     "rating":  8, "review_text": None},
    {"username": "alice", "title": "The Godfather", "rating": 10, "review_text": "A true classic."},
    {"username": "bob",   "title": "Spirited Away", "rating":  9, "review_text": None},
]

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
                  reviews
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

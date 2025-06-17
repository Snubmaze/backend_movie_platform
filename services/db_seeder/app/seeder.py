import asyncio
from sqlalchemy import text
from database import new_session

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
        "actors": [
            "Leonardo DiCaprio",
            "Joseph Gordon-Levitt",
            "Elliot Page"
        ],
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
        "actors": [
            "Marlon Brando",
            "Al Pacino"
        ],
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
        "actors": [
            "Rumi Hiiragi",
            "Miyu Irino"
        ],
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
        "actors": [
            "Song Kang-ho",
            "Lee Sun-kyun"
        ],
    },
]

async def seed():
    async with new_session() as session:
        async with session.begin():
            await session.execute(text("""
             TRUNCATE
               movie_actors,
               movie_directors,
               movie_countries,
               movie_genres,
               movies,
               actors,
               directors,
               countries
             RESTART IDENTITY CASCADE
            """))
            
            for name in {g for film in films for g in film["genres"]}:
                await session.execute(
                    text("INSERT INTO genres(name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                    {"name": name},
                )
            for name in {c for film in films for c in film["countries"]}:
                await session.execute(
                    text("INSERT INTO countries(name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                    {"name": name},
                )
            for name in {d for film in films for d in film["directors"]}:
                await session.execute(
                    text("INSERT INTO directors(full_name) VALUES (:name)"),
                    {"name": name},
                )
            for actor in {actor for film in films for actor in film["actors"]}:
                await session.execute(
                    text("INSERT INTO actors(full_name) VALUES (:name)"),
                    {"name": actor},
                )

            # 2) Фильмы и связи
            for film in films:
                existing = await session.scalar(
                    text("SELECT movie_id FROM movies WHERE title = :title"),
                    {"title": film["title"]},
                )
                if existing:
                    movie_id = existing
                else:
                    result = await session.execute(
                        text(
                            "INSERT INTO movies(title, description, release_year, duration_min, avg_rating, poster_url, trailer_url) "
                            "VALUES (:title, :description, :release_year, :duration_min, :avg_rating, :poster_url, :trailer_url) "
                            "RETURNING movie_id"
                        ),
                        film,
                    )
                    movie_id = result.scalar_one()

                # связи
                for name in film["genres"]:
                    gid = await session.scalar(text("SELECT genre_id FROM genres WHERE name = :name"), {"name": name})
                    await session.execute(
                        text("INSERT INTO movie_genres(movie_id, genre_id) VALUES (:mid, :gid) ON CONFLICT DO NOTHING"),
                        {"mid": movie_id, "gid": gid},
                    )
                for name in film["countries"]:
                    cid = await session.scalar(text("SELECT country_id FROM countries WHERE name = :name"), {"name": name})
                    await session.execute(
                        text("INSERT INTO movie_countries(movie_id, country_id) VALUES (:mid, :cid) ON CONFLICT DO NOTHING"),
                        {"mid": movie_id, "cid": cid},
                    )
                for name in film["directors"]:
                    did = await session.scalar(text("SELECT director_id FROM directors WHERE full_name = :name"), {"name": name})
                    await session.execute(
                        text("INSERT INTO movie_directors(movie_id, director_id) VALUES (:mid, :did) ON CONFLICT DO NOTHING"),
                        {"mid": movie_id, "did": did},
                    )
                for actor in film["actors"]:
                    aid = await session.scalar(text("SELECT actor_id FROM actors WHERE full_name = :name"), {"name": actor})
                    await session.execute(
                        text("INSERT INTO movie_actors(movie_id, actor_id) VALUES (:mid, :aid) ON CONFLICT DO NOTHING"),
                        {"mid": movie_id, "aid": aid},
                    )

if __name__ == "__main__":
    asyncio.run(seed())

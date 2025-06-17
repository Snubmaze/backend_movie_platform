from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.movies import Movie, MovieCreate, MovieUpdate
from typing import List


async def get_all_movies(session: AsyncSession) -> List[Movie]:
    result = await session.execute(text("""
    SELECT
      m.movie_id,
      m.title,
      m.description,
      m.release_year,
      m.duration_min,
      m.avg_rating,
      m.poster_url,
      m.trailer_url,
      -- агрегируем жанры
      COALESCE(json_agg(DISTINCT g.name)   FILTER (WHERE g.name   IS NOT NULL), '[]') AS genres,
      -- агрегируем актёров
      COALESCE(json_agg(DISTINCT a.full_name) FILTER (WHERE a.full_name IS NOT NULL), '[]') AS actors,
      -- агрегируем режиссёров
      COALESCE(json_agg(DISTINCT d.full_name) FILTER (WHERE d.full_name IS NOT NULL), '[]') AS directors,
      -- агрегируем страны
      COALESCE(json_agg(DISTINCT c.name)   FILTER (WHERE c.name   IS NOT NULL), '[]') AS countries
    FROM movies m
    LEFT JOIN movie_genres    mg ON mg.movie_id    = m.movie_id
    LEFT JOIN genres          g  ON g.genre_id     = mg.genre_id
    LEFT JOIN movie_actors    ma ON ma.movie_id    = m.movie_id
    LEFT JOIN actors          a  ON a.actor_id     = ma.actor_id
    LEFT JOIN movie_directors md ON md.movie_id    = m.movie_id
    LEFT JOIN directors       d  ON d.director_id  = md.director_id
    LEFT JOIN movie_countries mc ON mc.movie_id    = m.movie_id
    LEFT JOIN countries       c  ON c.country_id   = mc.country_id
    GROUP BY
      m.movie_id,
      m.title,
      m.description,
      m.release_year,
      m.duration_min,
      m.avg_rating,
      m.poster_url,
      m.trailer_url
    """))
    rows = result.mappings().all()
    return [Movie(**dict(row)) for row in rows]


# async def create_movie(db: AsyncSession, movie: MovieCreate) -> MovieRead:
#     insert_sql = text("""
#         INSERT INTO movies (title, description, release_year, duration_min)
#         VALUES ('{movie.title}', '{movie.description}', '{movie.release_year}', '{movie.duration_min}')
#     """)
#     result = await db.execute(insert_sql, movie.dict(exclude={"genre_ids","country_ids"}))
#     new_id = result.scalar_one()
#     if movie.genre_ids:
#         await db.execute(
#             text("""
#                 INSERT INTO movie_genres (movie_id, genre_id)
#                 SELECT :movie_id, genre_id FROM unnest(:genre_ids::int[]) AS genre_id
#             """),
#             {"movie_id": new_id, "genre_ids": movie.genre_ids}
#         )
#     if movie.country_ids:
#         await db.execute(
#             text("""
#                 INSERT INTO movie_countries (movie_id, country_id)
#                 SELECT :movie_id, country_id FROM unnest(:country_ids::int[]) AS country_id
#             """),
#             {"movie_id": new_id, "country_ids": movie.country_ids}
#         )
#     await db.commit()
#     return await get_movie(db, new_id)

# async def get_movie(db: AsyncSession, movie_id: int) -> MovieRead | None:
#     select_sql = text("""
#         SELECT 
#             m.movie_id, m.title, m.description, m.release_year, m.duration_min,
#             m.avg_rating, m.poster_url, m.trailer_url,
#             ARRAY_REMOVE(ARRAY_AGG(DISTINCT g.name), NULL) AS genres,
#             ARRAY_REMOVE(ARRAY_AGG(DISTINCT c.name), NULL) AS countries
#         FROM movies m
#         LEFT JOIN movie_genres mg ON mg.movie_id = m.movie_id
#         LEFT JOIN genres g       ON g.genre_id = mg.genre_id
#         LEFT JOIN movie_countries mc ON mc.movie_id = m.movie_id
#         LEFT JOIN countries c    ON c.country_id = mc.country_id
#         WHERE m.movie_id = :movie_id
#         GROUP BY m.movie_id
#     """)
#     result = await db.execute(select_sql, {"movie_id": movie_id})
#     row = result.first()
#     if not row:
#         return None
#     return MovieRead(
#         movie_id    = row.movie_id,
#         title       = row.title,
#         description = row.description,
#         release_year= row.release_year,
#         duration_min= row.duration_min,
#         avg_rating  = float(row.avg_rating or 0),
#         poster_url  = row.poster_url,
#         trailer_url = row.trailer_url,
#         genres      = row.genres or [],
#         countries   = row.countries or [],
#     )

# async def update_movie(db: AsyncSession, movie_id: int, movie: MovieCreate) -> MovieRead:
#     await db.execute(
#         text("""
#             UPDATE movies
#             SET title = :title,
#                 description = :description,
#                 release_year = :release_year,
#                 duration_min = :duration_min
#             WHERE movie_id = :movie_id
#         """),
#         {**movie.dict(exclude={"genre_ids","country_ids"}), "movie_id": movie_id}
#     )
#     await db.execute(text("DELETE FROM movie_genres WHERE movie_id = :movie_id"), {"movie_id": movie_id})
#     if movie.genre_ids:
#         await db.execute(
#             text("""
#                 INSERT INTO movie_genres (movie_id, genre_id)
#                 SELECT :movie_id, genre_id FROM unnest(:genre_ids::int[]) AS genre_id
#             """),
#             {"movie_id": movie_id, "genre_ids": movie.genre_ids}
#         )
#     await db.execute(text("DELETE FROM movie_countries WHERE movie_id = :movie_id"), {"movie_id": movie_id})
#     if movie.country_ids:
#         await db.execute(
#             text("""
#                 INSERT INTO movie_countries (movie_id, country_id)
#                 SELECT :movie_id, country_id FROM unnest(:country_ids::int[]) AS country_id
#             """),
#             {"movie_id": movie_id, "country_ids": movie.country_ids}
#         )
#     await db.commit()
#     return await get_movie(db, movie_id)

# async def delete_movie(db: AsyncSession, movie_id: int) -> None:
#     await db.execute(text("DELETE FROM movie_genres WHERE movie_id = :movie_id"), {"movie_id": movie_id})
#     await db.execute(text("DELETE FROM movie_countries WHERE movie_id = :movie_id"), {"movie_id": movie_id})
#     await db.execute(text("DELETE FROM movies WHERE movie_id = :movie_id"), {"movie_id": movie_id})
#     await db.commit()

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.content_service.schemas import MovieDetail, MovieUpdate, MovieSummary, MovieBase, MoviePatch
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select


async def get_all_movies(session: AsyncSession) -> List[MovieSummary]:
    result = await session.execute(text("""
        SELECT movie_id, title, release_year, avg_rating, poster_url
          FROM movies
          ORDER BY movie_id
    """))
    rows = result.mappings().all()
    return [MovieSummary(**dict(row)) for row in rows]


async def get_movie(session: AsyncSession, movie_id: int) -> Optional[MovieDetail]:
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
          COALESCE(json_agg(DISTINCT g.name)   FILTER (WHERE g.name   IS NOT NULL), '[]') AS genres,
          COALESCE(json_agg(DISTINCT a.full_name) FILTER (WHERE a.full_name IS NOT NULL), '[]') AS actors,
          COALESCE(json_agg(DISTINCT d.full_name) FILTER (WHERE d.full_name IS NOT NULL), '[]') AS directors,
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
        WHERE m.movie_id = :movie_id
        GROUP BY
          m.movie_id,
          m.title,
          m.description,
          m.release_year,
          m.duration_min,
          m.avg_rating,
          m.poster_url,
          m.trailer_url
    """), {"movie_id": movie_id})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Movie not found")
    return MovieDetail(**dict(row))


# async def patch_movie(
#     session: AsyncSession,
#     movie_id: int,
#     data: MoviePatch
# ) -> MovieDetail:
#     # 1) Обновляем колонки таблицы movies
#     #    — берем только те ключи, что реально есть в таблице
#     allowed = {
#         "title", "description", "release_year",
#         "duration_min", "avg_rating", "poster_url", "trailer_url"
#     }
#     upd = {k: v for k, v in data.dict(exclude_unset=True).items() if k in allowed}
#     if upd:
#         set_clause = ", ".join(f"{k} = :{k}" for k in upd)
#         await session.execute(
#             text(f"UPDATE movies SET {set_clause} WHERE movie_id = :movie_id"),
#             {**upd, "movie_id": movie_id}
#         )

#     # 2) Жанры
#     if data.genres is not None:
#         await session.execute(
#             text("DELETE FROM movie_genres WHERE movie_id = :mid"),
#             {"mid": movie_id}
#         )
#         for name in data.genres:
#             gid = await session.scalar(
#                 text("SELECT genre_id FROM genres WHERE name = :name"),
#                 {"name": name}
#             )
#             if gid is None:
#                 raise HTTPException(400, f"Genre '{name}' not found")
#             await session.execute(
#                 text("INSERT INTO movie_genres(movie_id, genre_id) VALUES (:mid, :gid)"),
#                 {"mid": movie_id, "gid": gid}
#             )

#     # 3) Страны — точно так же
#     if data.countries is not None:
#         await session.execute(
#             text("DELETE FROM movie_countries WHERE movie_id = :mid"),
#             {"mid": movie_id}
#         )
#         for name in data.countries:
#             cid = await session.scalar(
#                 text("SELECT country_id FROM countries WHERE name = :name"),
#                 {"name": name}
#             )
#             if cid is None:
#                 raise HTTPException(400, f"Country '{name}' not found")
#             await session.execute(
#                 text("INSERT INTO movie_countries(movie_id, country_id) VALUES (:mid, :cid)"),
#                 {"mid": movie_id, "cid": cid}
#             )

#     # 4) Актёры
#     if data.actors is not None:
#         await session.execute(
#             text("DELETE FROM movie_actors WHERE movie_id = :mid"),
#             {"mid": movie_id}
#         )
#         for full_name in data.actors:
#             aid = await session.scalar(
#                 text("SELECT actor_id FROM actors WHERE full_name = :name"),
#                 {"name": full_name}
#             )
#             if aid is None:
#                 raise HTTPException(400, f"Actor '{full_name}' not found")
#             await session.execute(
#                 text("INSERT INTO movie_actors(movie_id, actor_id) VALUES (:mid, :aid)"),
#                 {"mid": movie_id, "aid": aid}
#             )

#     # 5) Режиссёры
#     if data.directors is not None:
#         await session.execute(
#             text("DELETE FROM movie_directors WHERE movie_id = :mid"),
#             {"mid": movie_id}
#         )
#         for full_name in data.directors:
#             did = await session.scalar(
#                 text("SELECT director_id FROM directors WHERE full_name = :name"),
#                 {"name": full_name}
#             )
#             if did is None:
#                 raise HTTPException(400, f"Director '{full_name}' not found")
#             await session.execute(
#                 text("INSERT INTO movie_directors(movie_id, director_id) VALUES (:mid, :did)"),
#                 {"mid": movie_id, "did": did}
#             )

#     await session.commit()
#     # 6) Вернуть обновлённый объект
#     return await get_movie(session, movie_id)
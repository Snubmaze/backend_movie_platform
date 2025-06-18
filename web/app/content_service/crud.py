from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.content_service.schemas import Movie, MovieCreate, MovieUpdate, MovieSummary
from typing import List, Optional
from fastapi import HTTPException

async def get_all_movies(session: AsyncSession) -> List[Movie]:
    result = await session.execute(text("""
        SELECT movie_id, title, release_year, avg_rating, poster_url
          FROM movies
          ORDER BY movie_id
    """))
    rows = result.mappings().all()
    return [MovieSummary(**dict(row)) for row in rows]


async def get_movie(session: AsyncSession, movie_id: int) -> Optional[Movie]:
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
    return Movie(**dict(row))
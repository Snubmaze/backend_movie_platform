from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.content_service.movies.schemas import MovieDetail, MovieAttributesUpdate, MovieSummary, MovieCreate
from typing import List, Optional
from fastapi import HTTPException
from decimal import Decimal


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


async def create_movie(
    session: AsyncSession,
    payload: MovieCreate
) -> MovieDetail:
    # 1) Вставляем запись
    result = await session.execute(
        text("""
            INSERT INTO movies (
              title,
              description,
              release_year,
              duration_min,
              poster_url,
              trailer_url
            ) VALUES (
              :title,
              :description,
              :release_year,
              :duration_min,
              :poster_url,
              :trailer_url
            )
            RETURNING
              movie_id,
              title,
              release_year,
              avg_rating,
              description,
              duration_min,
              poster_url,
              trailer_url
        """),
        {
            "title": payload.title,
            "description": payload.description,
            "release_year": payload.release_year,
            "duration_min": payload.duration_min,
            "poster_url": payload.poster_url,
            "trailer_url": payload.trailer_url,
        }
    )
    await session.commit()

    row = result.first()
    if not row:
        raise HTTPException(
            status_code=500,
            detail="Failed to create movie"
        )

    data = row._mapping
    return MovieDetail(
        movie_id    = data["movie_id"],
        title       = data["title"],
        release_year= data["release_year"],
        avg_rating  = Decimal(data["avg_rating"]),
        description = data.get("description"),
        duration_min= data["duration_min"],
        poster_url  = data.get("poster_url"),
        trailer_url = data.get("trailer_url"),
        genres      = [],
        actors      = [],
        directors   = [],
        countries   = [],
    )


async def update_movie_attributes(
    session: AsyncSession,
    movie_id: int,
    payload: MovieAttributesUpdate
) -> MovieDetail:
    """
    Обновляет базовые поля фильма в таблице movies и возвращает актуальные данные.
    """
    # 1. Проверяем существование фильма
    existing = await get_movie(session, movie_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Movie not found")

    # 2. Формируем части запроса UPDATE
    update_fields = []
    params = {"movie_id": movie_id}
    for field in [
        "title", "description", "release_year",
        "duration_min", "poster_url", "trailer_url"
    ]:
        value = getattr(payload, field)
        if value is not None:
            update_fields.append(f"{field} = :{field}")
            params[field] = value

    # 3. Выполняем UPDATE, если есть поля для изменения
    if update_fields:
        sql = f"UPDATE movies SET {', '.join(update_fields)} WHERE movie_id = :movie_id"
        await session.execute(text(sql), params)
        await session.commit()

    # 4. Возвращаем обновлённые данные
    updated = await get_movie(session, movie_id)
    return updated


async def delete_movie(
    session: AsyncSession,
    movie_id: int
) -> dict:
    # 1) Проверяем, что фильм существует
    exists = await session.execute(
        text("SELECT 1 FROM movies WHERE movie_id = :movie_id"),
        {"movie_id": movie_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Movie not found")

    # 2) Удаляем все связи
    await session.execute(
        text("DELETE FROM movie_genres    WHERE movie_id = :movie_id"),
        {"movie_id": movie_id}
    )
    await session.execute(
        text("DELETE FROM movie_actors    WHERE movie_id = :movie_id"),
        {"movie_id": movie_id}
    )
    await session.execute(
        text("DELETE FROM movie_directors WHERE movie_id = :movie_id"),
        {"movie_id": movie_id}
    )
    await session.execute(
        text("DELETE FROM movie_countries WHERE movie_id = :movie_id"),
        {"movie_id": movie_id}
    )

    # 3) Удаляем сам фильм
    await session.execute(
        text("DELETE FROM movies WHERE movie_id = :movie_id"),
        {"movie_id": movie_id}
    )

    # 4) Коммитим изменения
    await session.commit()

    return {"status": 200, "detail": f"Movie {movie_id} successfully deleted"}
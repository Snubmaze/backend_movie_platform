from typing import List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.content_service.directors.schemas import DirectorCreate, DirectorRead

async def get_all_directors(session: AsyncSession) -> List[DirectorRead]:
    result = await session.execute(
        text("SELECT director_id, full_name, birth_date, photo_url FROM directors ORDER BY full_name")
    )
    rows = result.fetchall()
    return [DirectorRead(**row._mapping) for row in rows]

async def create_director(session: AsyncSession, director: DirectorCreate) -> DirectorRead:
    result = await session.execute(
        text("""
            INSERT INTO directors (full_name, birth_date, photo_url)
            VALUES (:full_name, :birth_date, :photo_url)
            RETURNING director_id, full_name, birth_date, photo_url
        """),
        {
            "full_name":  director.full_name,
            "birth_date": director.birth_date,
            "photo_url":  director.photo_url
        }
    )
    await session.commit()
    row = result.first()
    return DirectorRead(**row._mapping)

async def delete_director(session: AsyncSession, director_id: int) -> dict:
    exists = await session.execute(
        text("SELECT 1 FROM directors WHERE director_id = :did"),
        {"did": director_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(404, "Director not found")

    # сначала очистка связей
    await session.execute(
        text("DELETE FROM movie_directors WHERE director_id = :did"),
        {"did": director_id}
    )
    # потом удаление самого режиссёра
    await session.execute(
        text("DELETE FROM directors WHERE director_id = :did"),
        {"did": director_id}
    )
    await session.commit()
    return {"status": 200, "detail": f"Director {director_id} successfully deleted"}

async def add_movie_director(
    session: AsyncSession,
    movie_id: int,
    director_id: int
) -> dict:
    await session.execute(
        text(
            "INSERT INTO movie_directors(movie_id, director_id) "
            "VALUES(:movie_id, :director_id) "
            "ON CONFLICT DO NOTHING"
        ),
        {"movie_id": movie_id, "director_id": director_id}
    )
    return {"status": 200, "detail": f"Director {director_id} assigned to movie {movie_id}"}

async def remove_movie_director(
    session: AsyncSession,
    movie_id: int,
    director_id: int
) -> dict:
    await session.execute(
        text(
            "DELETE FROM movie_directors "
            "WHERE movie_id = :movie_id AND director_id = :director_id"
        ),
        {"movie_id": movie_id, "director_id": director_id}
    )
    return {"status": 200, "detail": f"Director {director_id} unassigned from movie {movie_id}"}

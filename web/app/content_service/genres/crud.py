from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.content_service.genres.schemas import GenreCreate, GenreRead
from fastapi import HTTPException
from typing import List

async def add_movie_genre(
    session: AsyncSession,
    movie_id: int,
    genre_id: int
):
    await session.execute(
        text(
            "INSERT INTO movie_genres(movie_id, genre_id) "
            "VALUES(:movie_id, :genre_id) "
            "ON CONFLICT DO NOTHING"
        ),
        {"movie_id": movie_id, "genre_id": genre_id}
    )
    return {"status_code": 200}


async def remove_movie_genre(
    session: AsyncSession,
    movie_id: int,
    genre_id: int
):
    await session.execute(
        text(
            "DELETE FROM movie_genres "
            "WHERE movie_id = :movie_id AND genre_id = :genre_id"
        ),
        {"movie_id": movie_id, "genre_id": genre_id}
    )
    return {"status_code": 200}


async def get_all_genres(session: AsyncSession) -> List[GenreRead]:
    result = await session.execute(
        text("SELECT genre_id, name FROM genres ORDER BY name")
    )
    rows = result.fetchall()
    return [GenreRead(**row._mapping) for row in rows]


async def create_genre(session: AsyncSession, genre: GenreCreate) -> GenreRead:
    genre_exist = await session.execute(
        text("SELECT 1 FROM genres WHERE name = :name"),
        {"name": genre.name}
    )
    if genre_exist.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Genre already exists")
    result = await session.execute(
        text("""
            INSERT INTO genres (name)
            VALUES (:name)
            RETURNING genre_id, name
        """),
        {"name": genre.name}
    )
    await session.commit()
    row = result.first()
    return GenreRead(**row._mapping)


async def delete_genre(session: AsyncSession, genre_id: int) -> dict:
    genre_exists = await session.execute(
        text("SELECT 1 FROM genres WHERE genre_id = :gid"),
        {"gid": genre_id}
    )
    if not genre_exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Genre not found")
    
    await session.execute(
        text("DELETE FROM movie_genres WHERE genre_id = :gid"),
        {"gid": genre_id}
    )
    
    await session.execute(
        text("DELETE FROM genres WHERE genre_id = :gid"),
        {"gid": genre_id}
    )
    await session.commit()
    return {"status_code": 200, "detail": f"Genre id = {genre_id} sunccesfully deleted"}
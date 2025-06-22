from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.content_service.actors.schemas import ActorCreate, ActorRead


async def get_all_actors(session: AsyncSession) -> List[ActorRead]:
    result = await session.execute(
        text("SELECT actor_id, full_name, birth_date, photo_url FROM actors ORDER BY full_name")
    )
    rows = result.fetchall()
    return [ActorRead(**row._mapping) for row in rows]


async def create_actor(session: AsyncSession, actor: ActorCreate) -> ActorRead:
    if actor.birth_date is not None:
        dup = await session.execute(
            text("""
                SELECT 1 
                  FROM actors 
                 WHERE full_name = :full_name 
                   AND birth_date = :birth_date
            """),
            {"full_name": actor.full_name, "birth_date": actor.birth_date}
        )
    else:
        dup = await session.execute(
            text("""
                SELECT 1 
                  FROM actors 
                 WHERE full_name = :full_name 
                   AND birth_date IS NULL
            """),
            {"full_name": actor.full_name}
        )
    if dup.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Actor with this name and birth date already exists"
        )

    result = await session.execute(
        text("""
            INSERT INTO actors (full_name, birth_date, photo_url)
            VALUES (:full_name, :birth_date, :photo_url)
            RETURNING actor_id, full_name, birth_date, photo_url
        """),
        {
            "full_name": actor.full_name,
            "birth_date": actor.birth_date,
            "photo_url": actor.photo_url
        }
    )
    await session.commit()
    row = result.first()
    return ActorRead(**row._mapping)


async def delete_actor(session: AsyncSession, actor_id: int) -> dict:
    exists = await session.execute(
        text("SELECT 1 FROM actors WHERE actor_id = :aid"),
        {"aid": actor_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Actor not found")

    await session.execute(
        text("DELETE FROM movie_actors WHERE actor_id = :aid"),
        {"aid": actor_id}
    )
    await session.execute(
        text("DELETE FROM actors WHERE actor_id = :aid"),
        {"aid": actor_id}
    )
    await session.commit()
    return {"detail": f"Actor {actor_id} successfully deleted"}


async def add_movie_actor(
    session: AsyncSession,
    movie_id: int,
    actor_id: int,
    character: Optional[str] = None
):
    await session.execute(
        text(
            "INSERT INTO movie_actors(movie_id, actor_id, character) "
            "VALUES(:movie_id, :actor_id, :character) "
            "ON CONFLICT (movie_id, actor_id) DO UPDATE "
            "SET character = EXCLUDED.character"
        ),
        {
            "movie_id": movie_id,
            "actor_id": actor_id,
            "character": character
        }
    )
    return {"status_code": 200}

async def remove_movie_actor(
    session: AsyncSession,
    movie_id: int,
    actor_id: int
):
    await session.execute(
        text(
            "DELETE FROM movie_actors "
            "WHERE movie_id = :movie_id AND actor_id = :actor_id"
        ),
        {"movie_id": movie_id, "actor_id": actor_id}
    )
    return {"status_code": 200}

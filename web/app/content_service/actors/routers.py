from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.content_service.movies.crud import get_movie
from app.database import get_session
from app.content_service.actors.schemas import ActorCreate, ActorRead
from app.content_service.actors.crud import (
    get_all_actors,
    create_actor,
    delete_actor,
    add_movie_actor,
    remove_movie_actor
)


router = APIRouter(tags=["Content"])


@router.get("/actors")
async def list_actors(session: AsyncSession = Depends(get_session)):
    return await get_all_actors(session)


@router.post("/actors", response_model=ActorRead)
async def add_actor(
    payload: ActorCreate,
    session: AsyncSession = Depends(get_session)
):
    return await create_actor(session, payload)


@router.delete("/actors/{actor_id}", response_model=Dict[str, str])
async def remove_actor(
    actor_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await delete_actor(session, actor_id)


@router.post("/movies/{movie_id}/actors/{actor_id}")
async def assign_actor_to_movie(
    movie_id: int,
    actor_id: int,
    character: Optional[str] = Query(
        None,
        description="Имя персонажа, которого играет актёр"
    ),
    session: AsyncSession = Depends(get_session)
):
    movie = await get_movie(session, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    # Проверяем актёра
    exists = await session.execute(
        text("SELECT 1 FROM actors WHERE actor_id = :aid"),
        {"aid": actor_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Actor not found")
    # Добавляем/обновляем связь
    result = await add_movie_actor(session, movie_id, actor_id, character)
    await session.commit()
    return result


@router.delete("/movies/{movie_id}/actors/{actor_id}")
async def unassign_actor_from_movie(
    movie_id: int,
    actor_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Проверяем фильм
    movie = await get_movie(session, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    # Проверяем актёра
    exists = await session.execute(
        text("SELECT 1 FROM actors WHERE actor_id = :aid"),
        {"aid": actor_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Actor not found")
    # Удаляем связь
    result = await remove_movie_actor(session, movie_id, actor_id)
    await session.commit()
    return result


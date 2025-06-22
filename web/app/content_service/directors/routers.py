from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.content_service.movies.crud import get_movie
from app.database import get_session
from app.dependencies import get_admin
from app.auth_service.schemas import UserRead
from app.content_service.directors.schemas import DirectorCreate, DirectorRead
from app.content_service.directors.crud import (
    get_all_directors,
    create_director,
    delete_director,
    add_movie_director,
    remove_movie_director
)


router = APIRouter(tags=["Content"])


@router.get("/directors", response_model=List[DirectorRead])
async def list_directors(session: AsyncSession = Depends(get_session)):
    return await get_all_directors(session)


@router.post("/directors", response_model=DirectorRead)
async def add_director(
    payload: DirectorCreate,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    return await create_director(session, payload)


@router.delete("/directors/{director_id}", response_model=Dict[str, str])
async def remove_director(
    director_id: int,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    return await delete_director(session, director_id)


@router.post("/movies/{movie_id}/directors/{director_id}", response_model=Dict[str, str])
async def assign_director_to_movie(
    movie_id: int,
    director_id: int,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    movie = await get_movie(session, movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    exists = await session.execute(
        text("SELECT 1 FROM directors WHERE director_id = :did"),
        {"did": director_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(404, "Director not found")

    result = await add_movie_director(session, movie_id, director_id)
    await session.commit()
    return result


@router.delete("/movies/{movie_id}/directors/{director_id}", response_model=Dict[str, str])
async def unassign_director_from_movie(
    movie_id: int,
    director_id: int,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    movie = await get_movie(session, movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    exists = await session.execute(
        text("SELECT 1 FROM directors WHERE director_id = :did"),
        {"did": director_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(404, "Director not found")

    result = await remove_movie_director(session, movie_id, director_id)
    await session.commit()
    return result

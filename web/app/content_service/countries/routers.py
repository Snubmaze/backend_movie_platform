from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_admin
from app.auth_service.schemas import UserRead
from app.database import get_session
from app.content_service.countries.schemas import CountryCreate, CountryRead
from app.content_service.countries.crud import (
    get_all_countries,
    create_country,
    delete_country,
    add_movie_country,
    remove_movie_country
)
from app.content_service.movies.crud import get_movie


router = APIRouter(tags=["Content"])


@router.get("/countries", response_model=List[CountryRead])
async def list_countries(session: AsyncSession = Depends(get_session)):
    return await get_all_countries(session)


@router.post("/countries", response_model=CountryRead)
async def add_country(
    payload: CountryCreate,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    return await create_country(session, payload)


@router.delete("/countries/{country_id}", response_model=Dict[str, str])
async def remove_country(
    country_id: int,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    return await delete_country(session, country_id)


@router.post("/movies/{movie_id}/countries/{country_id}", response_model=Dict[str, str])
async def assign_country_to_movie(
    movie_id: int,
    country_id: int,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    movie = await get_movie(session, movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    exists = await session.execute(
        text("SELECT 1 FROM countries WHERE country_id = :cid"),
        {"cid": country_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(404, "Country not found")

    result = await add_movie_country(session, movie_id, country_id)
    await session.commit()
    return result


@router.delete("/movies/{movie_id}/countries/{country_id}", response_model=Dict[str, str])
async def unassign_country_from_movie(
    movie_id: int,
    country_id: int,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    movie = await get_movie(session, movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    exists = await session.execute(
        text("SELECT 1 FROM countries WHERE country_id = :cid"),
        {"cid": country_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(404, "Country not found")

    result = await remove_movie_country(session, movie_id, country_id)
    await session.commit()
    return result

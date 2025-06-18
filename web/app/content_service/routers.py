from app.content_service.crud import get_all_movies, get_movie
from fastapi import APIRouter, Depends
from app.content_service.schemas import Movie, MovieSummary
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session


router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
    )

@router.get("/", response_model=List[MovieSummary])
async def read_movies(session: AsyncSession = Depends(get_session)):
    return await get_all_movies(session)


@router.get("/{movie_id}", response_model=Movie)
async def read_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    result = await get_movie(session, movie_id)
    return result
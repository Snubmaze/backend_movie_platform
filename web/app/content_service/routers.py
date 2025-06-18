from app.content_service.crud import get_all_movies, get_movie
from fastapi import APIRouter, Depends
from app.content_service.schemas import MovieDetail, MovieSummary, MovieUpdate, MoviePatch
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


@router.get("/{movie_id}", response_model=MovieDetail)
async def read_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    result = await get_movie(session, movie_id)
    return result

# @router.put("/{movie_id}", response_model=MovieDetail)
# async def put_movie(
#     movie_id: int,
#     payload: MovieUpdate,
#     session: AsyncSession = Depends(get_session)
# ):
#     return await update_movie(session, movie_id, payload)


# @router.patch("/{movie_id}", response_model=MovieDetail)
# async def patch_movie_endpoint(
#     movie_id: int,
#     payload: MoviePatch,
#     session: AsyncSession = Depends(get_session)
# ):
#     return await patch_movie(session, movie_id, payload)
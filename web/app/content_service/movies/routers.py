from app.content_service.movies.crud import get_all_movies, get_movie, update_movie_attributes, create_movie, delete_movie
from fastapi import APIRouter, Depends
from app.content_service.movies.schemas import MovieDetail, MovieSummary, MovieAttributesUpdate, MovieCreate
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.dependencies import get_admin
from typing import Dict


router = APIRouter(
    prefix="/movies",
    tags=["Content"]
    )

@router.get("/", response_model=List[MovieSummary])
async def read_movies(session: AsyncSession = Depends(get_session)):
    return await get_all_movies(session)


@router.get("/{movie_id}", response_model=MovieDetail)
async def read_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    result = await get_movie(session, movie_id)
    return result


@router.post("/", response_model=MovieDetail)
async def add_movie(
    payload: MovieCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Создаёт фильм с минимальным набором полей.
    Все связи (жанры, актёры и т.д.) добавляются через отдельные эндпоинты.
    """
    return await create_movie(session, payload)


@router.patch(
    "/{movie_id}/attributes",
    response_model=MovieDetail,
)
async def update_movie_attributes_endpoint(
    movie_id: int,
    payload: MovieAttributesUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Обновляет основные поля фильма: название, описание, год выпуска,
    продолжительность, ссылки на постер и трейлер.
    """
    return await update_movie_attributes(session, movie_id, payload)


@router.delete("/{movie_id}", response_model=Dict[str, str])
async def remove_movie(
    movie_id: int, 
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    return await delete_movie(session, movie_id)
from app.content_service.movies.crud import get_movies_filtered, get_movie, update_movie_attributes, create_movie, delete_movie
from fastapi import APIRouter, Depends, Query
from app.content_service.movies.schemas import MovieDetail, MovieSummary, MovieAttributesUpdate, MovieCreate
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.dependencies import get_admin
from typing import Dict
from app.auth_service.schemas import UserRead

router = APIRouter(
    prefix="/movies",
    tags=["Content"]
    )

@router.get("", response_model=List[MovieSummary])
async def read_movies(
    genre:    Optional[str] = Query(None, description="Начало названия жанра"),
    actor:    Optional[str] = Query(None, description="Начало имени актёра"),
    director: Optional[str] = Query(None, description="Начало имени режиссёра"),
    country:  Optional[str] = Query(None, description="Начало названия страны"),
    session:  AsyncSession  = Depends(get_session),
):
    """
    Список фильмов. Опциональная фильтрация по жанру, актёру, режиссёру или стране.
    Сортировка по убыванию среднего рейтинга.
    Если параметров нет — вернёт все (до 100 штук).
    """
    return await get_movies_filtered(session, genre, actor, director, country)


@router.get("/{movie_id}", response_model=MovieDetail)
async def read_movie(movie_id: int, session: AsyncSession = Depends(get_session)):
    result = await get_movie(session, movie_id)
    return result


@router.post("/", response_model=MovieDetail)
async def add_movie(
    payload: MovieCreate,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    return await create_movie(session, payload)


@router.patch(
    "/{movie_id}/attributes",
    response_model=MovieDetail,
)
async def update_movie_attributes_endpoint(
    movie_id: int,
    payload: MovieAttributesUpdate,
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
):
    """
    Обновляет основные поля фильма: название, описание, год выпуска,
    продолжительность, ссылки на постер и трейлер.
    """
    return await update_movie_attributes(session, movie_id, payload)


@router.delete("/{movie_id}", response_model=Dict[str, str])
async def remove_movie(
    movie_id: int, 
    session: AsyncSession = Depends(get_session),
    admin: UserRead = Depends(get_admin)
) -> Dict[str, str]:
    return await delete_movie(session, movie_id)
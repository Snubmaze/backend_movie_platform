from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.content_service.movies.crud import get_movie
from app.database import get_session
from app.content_service.genres.crud import add_movie_genre, remove_movie_genre, get_all_genres, create_genre, delete_genre
from app.content_service.genres.schemas import GenreCreate, GenreRead
from typing import List, Dict


router = APIRouter(tags=["Content"])


@router.get("/genres", response_model=List[GenreRead])
async def list_genres(session: AsyncSession = Depends(get_session)):
    return await get_all_genres(session)


@router.post("/genres", response_model=GenreRead)
async def add_genre(
    genre: GenreCreate,
    session: AsyncSession = Depends(get_session)
):
    return await create_genre(session, genre)


@router.delete("/genres/{genre_id}", response_model=Dict[str, str])
async def remove_genre(
    genre_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await delete_genre(session, genre_id)


@router.post("/movies/{movie_id}/genres/{genre_id}")
async def add_genre_to_movie(
    movie_id: int,
    genre_id: int,
    session: AsyncSession = Depends(get_session)
):
    movie = await get_movie(session, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    result = await session.execute(
        text("SELECT 1 FROM genres WHERE genre_id = :genre_id"),
        {"genre_id": genre_id}
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Genre not found")
    
    response = await add_movie_genre(session, movie_id, genre_id)
    await session.commit()
    return response


@router.delete("/movies/{movie_id}/genres/{genre_id}")
async def remove_genre_from_movie(
    movie_id: int,
    genre_id: int,
    session: AsyncSession = Depends(get_session)
):
    movie = await get_movie(session, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    result = await session.execute(
        text("SELECT 1 FROM genres WHERE genre_id = :genre_id"),
        {"genre_id": genre_id}
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Genre not found")
        
    response = await remove_movie_genre(session, movie_id, genre_id)
    await session.commit()
    return response


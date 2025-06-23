from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.dependencies import get_current_user
from app.favorites_service.crud import add_to_favorites, remove_from_favorites, get_user_favorites
from app.content_service.movies.schemas import MovieSummary
from typing import List


router = APIRouter(tags=["Favorites"])


@router.get("/favorites", response_model=List[MovieSummary])
async def list_favorites(
    current_user = Depends(get_current_user),
    session: AsyncSession  = Depends(get_session),
) -> List[MovieSummary]:
    return await get_user_favorites(session, current_user.user_id)

@router.post("/movies/{movie_id}/favorite")
async def add_fav(movie_id: int, current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await add_to_favorites(session, current_user.user_id, movie_id)

@router.delete("/movies/{movie_id}/favorite")
async def remove_fav(movie_id: int, current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await remove_from_favorites(session, current_user.user_id, movie_id)


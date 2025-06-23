from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.dependencies import get_current_user
from app.favorite_service.crud import add_to_favorites, remove_from_favorites

router = APIRouter(tags=["Favorites"])

@router.post("/movies/{movie_id}/favorite")
async def add_fav(movie_id: int, current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await add_to_favorites(session, current_user.user_id, movie_id)
    return {"status": "added to favorites"}

@router.delete("/movies/{movie_id}/favorite")
async def remove_fav(movie_id: int, current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await remove_from_favorites(session, current_user.user_id, movie_id)
    return {"status": "removed from favorites"}

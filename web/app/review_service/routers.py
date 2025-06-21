from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user
from app.review_service.schemas import ReviewCreate, ReviewRead
from app.review_service.crud import upsert_review, delete_review

router = APIRouter(tags=["Reviews"])

@router.post("/movies/{movie_id}/reviews", response_model=ReviewRead)
async def add_or_update_review(
    movie_id: int,
    payload: ReviewCreate,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await upsert_review(session, current_user.user_id, movie_id, payload)


@router.delete("/movies/{movie_id}/reviews", response_model=Dict[str, Any])
async def remove_review(
    movie_id: int,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await delete_review(session, current_user.user_id, movie_id)

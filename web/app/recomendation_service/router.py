from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user
from app.recommendation.schemas import MovieRead
from app.recommendation.crud import get_recommendations

router = APIRouter(tags=["Recommendations"])

@router.get("/recommendations", response_model=List[MovieRead])
async def recommendations(
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = 20
):
    return await get_recommendations(session, current_user.user_id, limit)

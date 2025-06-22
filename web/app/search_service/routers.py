from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.search_service.crud import search_movies_by_title
from app.content_service.movies.schemas import MovieSummary

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/movies", response_model=List[MovieSummary])
async def search_movies(
    q: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_session),
):
    return await search_movies_by_title(session, q)

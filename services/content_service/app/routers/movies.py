from app.crud.movies import get_all_movies
from fastapi import APIRouter, Depends
from app.schemas.movies import Movie
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_session


router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
    )

@router.get("/", response_model=List[Movie])
async def read_movies(session: AsyncSession = Depends(get_session)):
    return await get_all_movies(session)
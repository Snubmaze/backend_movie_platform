from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.content_service.movies.schemas import MovieSummary
from typing import List, Dict

async def get_user_favorites(
    session: AsyncSession, 
    user_id: int
) -> List[MovieSummary]:
    try:
        result = await session.execute(
            text("""
                SELECT
                  m.movie_id,
                  m.title,
                  m.release_year,
                  m.avg_rating,
                  m.poster_url
                FROM favorites f
                JOIN movies m ON m.movie_id = f.movie_id
                WHERE f.user_id = :uid
                ORDER BY f.added_at DESC
            """),
            {"uid": user_id}
        )
        rows = result.mappings().all()
        return [MovieSummary(**row) for row in rows]
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not fetch favorites"
        )


async def add_to_favorites(
    session: AsyncSession, 
    user_id: int, 
    movie_id: int
) -> Dict[str, str]:
    try:
        await session.execute(
            text("""
                INSERT INTO favorites (user_id, movie_id)
                VALUES (:uid, :mid)
                ON CONFLICT DO NOTHING
            """),
            {"uid": user_id, "mid": movie_id}
        )
        await session.commit()
        return {"status_code": 200, "detail": "success"}
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to add to favorites"
        )


async def remove_from_favorites(
    session: AsyncSession, 
    user_id: int, 
    movie_id: int
) -> Dict[str, str]:
    try:
        result = await session.execute(
            text("""
                DELETE FROM favorites 
                 WHERE user_id = :uid 
                   AND movie_id = :mid
            """),
            {"uid": user_id, "mid": movie_id}
        )
        await session.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404, 
                detail="Favorite entry not found"
            )
        return {"status_code": 200, "detail": "success"}
    except HTTPException:
        raise HTTPException(
                status_code=404, 
                detail="Favorite entry not found"
            )
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to remove from favorites"
        )

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

async def add_to_favorites(session: AsyncSession, user_id: int, movie_id: int):
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
    except:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to add to favorites")

async def remove_from_favorites(session: AsyncSession, user_id: int, movie_id: int):
    await session.execute(
        text("DELETE FROM favorites WHERE user_id = :uid AND movie_id = :mid"),
        {"uid": user_id, "mid": movie_id}
    )
    await session.commit()

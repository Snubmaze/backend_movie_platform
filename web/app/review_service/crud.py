from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.review_service.schemas import ReviewCreate, ReviewRead

async def upsert_review(
    session: AsyncSession,
    user_id: int,
    movie_id: int,
    payload: ReviewCreate
) -> ReviewRead:
    await session.execute(
        text("""
        INSERT INTO reviews (user_id, movie_id, rating, review_text)
        VALUES (:uid, :mid, :rating, :text)
        ON CONFLICT (user_id, movie_id) DO UPDATE
          SET rating      = EXCLUDED.rating,
              review_text = EXCLUDED.review_text,
              updated_at  = CURRENT_TIMESTAMP
        """),
        {
            "uid":     user_id,
            "mid":     movie_id,
            "rating":  payload.rating,
            "text":    payload.review_text
        }
    )
    await session.commit()


    result = await session.execute(
        text("""
        SELECT review_id, user_id, movie_id, rating, review_text, created_at, updated_at
          FROM reviews
         WHERE user_id = :uid AND movie_id = :mid
        """),
        {"uid": user_id, "mid": movie_id}
    )
    row = result.first()
    if not row:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось сохранить отзыв"
        )
    return ReviewRead(**row._mapping)

async def delete_review(
    session: AsyncSession,
    user_id: int,
    movie_id: int
) -> dict:

    exists = await session.execute(
        text("SELECT 1 FROM reviews WHERE user_id = :uid AND movie_id = :mid"),
        {"uid": user_id, "mid": movie_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Review not found")


    await session.execute(
        text("DELETE FROM reviews WHERE user_id = :uid AND movie_id = :mid"),
        {"uid": user_id, "mid": movie_id}
    )
    await session.commit()
    return {"status_code": 200, "deatail": "Review deleted"}

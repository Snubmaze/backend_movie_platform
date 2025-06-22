from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.subscription_service.payments.schemas import PaymentRead


async def complete_payment(
    session: AsyncSession,
    user_id: int,
    subscription_id: int
) -> PaymentRead:
    result = await session.execute(
        text("""
        UPDATE payments
           SET status   = 'completed',
               paid_at  = CURRENT_TIMESTAMP
         WHERE user_id         = :uid
           AND subscription_id = :sid
           AND status          = 'pending'
        RETURNING payment_id, user_id, subscription_id, amount, paid_at, status
        """),
        {"uid": user_id, "sid": subscription_id}
    )
    await session.commit()
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=400,
            detail="Нет ожидающего платежа для этой подписки"
        )
    return PaymentRead(**row._mapping)

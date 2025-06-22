from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.subscription_service.subscriptions.schemas import SubscriptionRead

async def create_subscription(
    session: AsyncSession,
    user_id: int,
    plan_id: int
) -> SubscriptionRead:
    # 1) Получаем параметры плана
    plan_res = await session.execute(
        text("""
        SELECT period_days, price
          FROM subscription_plans
         WHERE plan_id = :pid
        """),
        {"pid": plan_id}
    )
    plan_row = plan_res.first()
    if not plan_row:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Unknown plan_id")
    plan = plan_row._mapping

    # 2) Вычисляем даты
    start = date.today()
    end   = start + timedelta(days=plan["period_days"])

    # 3) Вставляем подписку в статусе 'pending'
    sub_res = await session.execute(
        text("""
        INSERT INTO subscriptions
          (user_id, plan_id, start_date, end_date, status, price_paid)
        VALUES
          (:uid, :pid, :start, :end, 'pending', :price)
        RETURNING subscription_id, user_id, plan_id, start_date, end_date, status, price_paid
        """),
        {
            "uid":   user_id,
            "pid":   plan_id,
            "start": start,
            "end":   end,
            "price": Decimal(plan["price"])
        }
    )
    sub_row = sub_res.first()
    if not sub_row:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать подписку"
        )
    subscription = sub_row._mapping

    # 4) Сразу создаем запись платежа со статусом 'pending'
    pay_res = await session.execute(
        text("""
        INSERT INTO payments
          (user_id, subscription_id, amount, status)
        VALUES
          (:uid, :sid, :amount, 'pending')
        RETURNING payment_id
        """),
        {
            "uid":    user_id,
            "sid":    subscription['subscription_id'],
            "amount": Decimal(plan["price"])
        }
    )
    await session.commit()

    return SubscriptionRead(**subscription)

async def cancel_subscription(
    session: AsyncSession,
    subscription_id: int,
    user_id: int
) -> dict[str, int]:
    res = await session.execute(
        text("""
        SELECT 1 FROM subscriptions
         WHERE subscription_id = :sid
           AND user_id = :uid
        """),
        {"sid": subscription_id, "uid": user_id}
    )
    if not res.scalar_one_or_none():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    await session.execute(
        text("""
        UPDATE subscriptions
           SET status = 'cancelled'
         WHERE subscription_id = :sid
        """),
        {"sid": subscription_id}
    )
    await session.commit()
    return {
        "status":          200,
        "subscription_id": subscription_id,
        "user_id":         user_id
    }

async def get_subscription_for_user(
    session: AsyncSession,
    user_id: int
) -> SubscriptionRead:
    """
    Возвращает последнюю подписку пользователя (по максимальному end_date),
    чтобы можно было узнать её статус, даты начала/окончания и сумму.
    """
    result = await session.execute(
        text("""
        SELECT
          subscription_id,
          user_id,
          plan_id,
          start_date,
          end_date,
          status,
          price_paid
        FROM subscriptions
        WHERE user_id = :uid
        ORDER BY end_date DESC
        LIMIT 1
        """),
        {"uid": user_id}
    )
    row = result.first()
    if not row:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="No subscriptions found for this user"
        )
    return SubscriptionRead(**row._mapping)
from typing import Any, Dict
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user
from app.subscription_service.subscriptions.schemas import SubscriptionCreate, SubscriptionRead
from app.subscription_service.subscriptions.crud import (
    get_subscription_for_user,
    create_subscription,
    cancel_subscription
)

router = APIRouter()


@router.get("/subscriptions", response_model=SubscriptionRead, summary="Текущая активная подписка")
async def read_subscription(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    sub = await get_subscription_for_user(session, current_user.user_id)
    if not sub:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No active subscription")
    return sub

@router.post("/subscriptions", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED,
             summary="Создать новую подписку")
async def add_subscription(
    payload: SubscriptionCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await create_subscription(session, current_user.user_id, payload.plan_id)

@router.patch("/subscriptions/{subscription_id}/cancel", response_model=Dict[str, Any],
              summary="Отменить подписку")
async def remove_subscription(
    subscription_id: int,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await cancel_subscription(session, subscription_id, current_user.user_id)
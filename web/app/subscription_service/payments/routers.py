from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import get_current_user
from app.subscription_service.payments.schemas import PaymentCreate, PaymentRead
from app.subscription_service.payments.crud import complete_payment

router = APIRouter()

@router.post("/payments", response_model=PaymentRead)
async def add_payment(
    payload: PaymentCreate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    return await complete_payment(
        session,
        current_user.user_id,
        payload.subscription_id
    )

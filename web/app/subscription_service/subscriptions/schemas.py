from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

class SubscriptionCreate(BaseModel):
    plan_id: int = Field(..., description="ID выбранного тарифного плана")

class SubscriptionRead(BaseModel):
    subscription_id: int   = Field(..., description="ID подписки")
    user_id:         int   = Field(..., description="ID пользователя")
    plan_id:         int   = Field(..., description="ID тарифного плана")
    start_date:      date  = Field(..., description="Дата начала подписки")
    end_date:        date  = Field(..., description="Дата окончания подписки")
    status:          str   = Field(..., description="Статус подписки (pending/active/expired)")
    price_paid:      Decimal = Field(..., description="Сумма, оплаченная за подписку")

    class Config:
        orm_mode = True

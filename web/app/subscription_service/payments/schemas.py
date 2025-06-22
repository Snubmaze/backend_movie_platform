from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    subscription_id: int

class PaymentRead(BaseModel):
    payment_id:      int
    user_id:         int
    subscription_id: int
    amount:          Decimal
    paid_at:         datetime
    status:          str

    class Config:
        orm_mode = True

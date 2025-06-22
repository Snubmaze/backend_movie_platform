from typing import Optional
from pydantic import BaseModel
from datetime import date

class ActorCreate(BaseModel):
    full_name: str
    birth_date: Optional[date] = None
    photo_url: Optional[str] = None

class ActorRead(BaseModel):
    actor_id: int
    full_name: str
    birth_date: Optional[date]
    photo_url: Optional[str]

    class Config:
        orm_mode = True

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class FavoriteRead(BaseModel):
    user_id: int
    movie_id: int
    added_at: datetime

    class Config:
        orm_mode = True

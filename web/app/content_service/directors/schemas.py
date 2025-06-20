from typing import Optional
from pydantic import BaseModel, Field
from datetime import date

class DirectorCreate(BaseModel):
    full_name: str = Field(..., description="Полное имя режиссёра")
    birth_date: Optional[date] = Field(None, description="Дата рождения")
    photo_url: Optional[str]    = Field(None, description="URL фотографии")

class DirectorRead(BaseModel):
    director_id: int
    full_name:   str
    birth_date:  Optional[date]
    photo_url:   Optional[str]

    class Config:
        orm_mode = True

from pydantic import BaseModel
from typing import Optional

class MovieRead(BaseModel):
    movie_id: int
    title: str
    description: Optional[str]
    release_year: int
    duration_min: int
    avg_rating: float
    poster_url: Optional[str]
    trailer_url: Optional[str]
    subscription_required: bool
    favorites_count: int

    class Config:
        orm_mode = True

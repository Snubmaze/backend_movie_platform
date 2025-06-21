from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=0, le=10)
    review_text: Optional[str] = Field(None, max_length=500)

class ReviewRead(ReviewCreate):
    review_id:   int
    user_id:     int
    movie_id:    int
    created_at:  datetime
    updated_at:  Optional[datetime]

    class Config:
        orm_mode = True

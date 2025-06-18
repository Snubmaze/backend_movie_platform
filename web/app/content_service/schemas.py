from pydantic import BaseModel, Field
from typing import List, Optional


class MovieBase(BaseModel):
    title: str = Field(..., description="Название фильма")
    description: Optional[str] = Field(None, description="Описание")
    release_year: int = Field(..., ge=1888, le=2100, description="Год выхода")
    duration_min: int = Field(..., gt=0, description="Длительность (мин)")
    avg_rating: Optional[float] = Field(0.0, ge=0.0, le=10.0, description="Средний рейтинг")
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None


class MovieSummary(BaseModel):
    movie_id: int
    title: str = Field(..., description="Название фильма")
    release_year: int = Field(..., ge=1888, le=2100, description="Год выхода")
    avg_rating: Optional[float] = Field(0.0, ge=0.0, le=10.0, description="Средний рейтинг")
    poster_url: Optional[str] = None


class Movie(MovieBase):
    movie_id: int
    genres:    List[str]
    actors:    List[str]
    directors: List[str]
    countries: List[str]


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1888, le=2100)
    duration_min: Optional[int] = Field(None, gt=0)
    avg_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None

    class Config:
        orm_mode = True

from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: int = Field(ge=1888, le=2100)
    duration_min: int = Field(gt=0)
    avg_rating: Decimal = Field(ge=0, le=10)
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    subscription_required: bool = Field(False)
    favorites_count: int = Field(0)


class MovieSummary(BaseModel):
    movie_id: int
    title: str
    release_year: int = Field(ge=1888, le=2100)
    avg_rating: Decimal
    poster_url: Optional[str] = None


class MovieDetail(MovieBase):
    movie_id: int
    genres:    List[str]
    actors:    List[str]
    directors: List[str]
    countries: List[str]


class MovieCreate(BaseModel):
    title:        str
    description:  Optional[str] = None
    release_year: int = Field(..., ge=1888)
    duration_min: int = Field(..., gt=0)
    poster_url:   Optional[str] = None
    trailer_url:  Optional[str] = None
    subscription_required: bool = Field(False)


class MovieAttributesUpdate(BaseModel):
    title: Optional[str]        = None
    description: Optional[str]  = None
    release_year: Optional[int] = Field(None, ge=1800, le=2100)
    duration_min: Optional[int] = Field(None, gt=0)
    poster_url: Optional[str]   = None
    trailer_url: Optional[str]  = None
    subscription_required: bool = Field(False)


    class Config:
        orm_mode = True


from pydantic import BaseModel, Field

class CountryCreate(BaseModel):
    name: str = Field(..., description="Название страны")

class CountryRead(BaseModel):
    country_id: int
    name:       str

    class Config:
        orm_mode = True

from pydantic import BaseModel

class GenreCreate(BaseModel):
    name: str

class GenreRead(BaseModel):
    genre_id: int
    name:     str

    class Config:
        orm_mode = True

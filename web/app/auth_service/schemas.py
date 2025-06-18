from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class LoginRequest(BaseModel):
    uername: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserBase(BaseModel):
    username: str = Field(..., description="Username пользователя")
    avatar_url: Optional[str]   = Field(None, description="URL аватара")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Пароль")

class UserRead(UserBase):
    user_id: int = Field(..., description="ID пользователя")
    role: str = Field(..., description="Роль пользователя")
    created_at: datetime = Field(..., description="Время создания")

    class Config:
        orm_mode = True
from pydantic import BaseSettings, BaseModel
from typing import Optional

class DatabaseSettings(BaseSettings):
    database_url: str


class JWTSettings(BaseSettings):
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    secret_key: str


class CookieSettings(BaseModel):
    httponly: bool = False
    secure: bool = False
    samesite: str = "Lax"
    domain: Optional[str] = None
    path: str = "/"


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()
    cookie: CookieSettings = CookieSettings()


settings = Settings()

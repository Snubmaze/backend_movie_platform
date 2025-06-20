from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.config import settings
from app.auth_service.schemas import TokenInfo


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.jwt.secret_key
ALGORITHM = settings.jwt.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.jwt.refresh_token_expire_days


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"purpose": "access", "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"purpose": "refresh", "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_pair_jwt(data: dict) -> TokenInfo:
    access = create_access_token(data)
    refresh = create_refresh_token(data)
    return TokenInfo(access_token=access, refresh_token=refresh)


def decode_jwt(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
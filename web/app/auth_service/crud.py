from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.auth_service.schemas import UserRead, UserCreate
from app.security import hash_password


async def get_user_by_username(
    username: str,
    session: AsyncSession
) -> Optional[UserRead]:

    q = text("""
        SELECT
          user_id,
          username,
          avatar_url,
          role,
          created_at
        FROM users
        WHERE username = :username
    """)
    result = await session.execute(q, {"username": username})
    row = result.first()
    return UserRead(**row._mapping) if row else None


async def add_user(
    user: UserCreate,
    session: AsyncSession
) -> UserRead:

    exists = await session.execute(
        text("SELECT 1 FROM users WHERE username = :username"),
        {"username": user.username}
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="username already registered")

    # 2) Вставляем нового пользователя
    pw_hash = hash_password(user.password)
    insert = text("""
        INSERT INTO users (
          username,
          password_hash,
          avatar_url
        ) VALUES (
          :username,
          :password_hash,
          :avatar_url
        )
        RETURNING
          user_id,
          username,
          avatar_url,
          role,
          created_at
    """)
    params = {
        "username":         user.username,
        "password_hash": pw_hash,
        "avatar_url":    user.avatar_url,
    }
    result = await session.execute(insert, params)
    await session.commit()
    row = result.first()
    return UserRead(**row._mapping)

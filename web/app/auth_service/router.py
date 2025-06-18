from app.auth_service.crud import get_user_by_username, add_user
from fastapi import APIRouter, Depends, HTTPException
from app.auth_service.schemas import UserCreate, UserBase, UserRead, TokenInfo
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.security import create_access_token, decode_access_token, verify_password, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register/", response_model=TokenInfo,)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    existing_user = await get_user_by_username(user.username, session)
    if existing_user:
        raise HTTPException(status_code=400, detail="username already taken")  

    await add_user(user, session)
    
    access_token = create_access_token(
        data={
            "sub": user.username, 
            }
        )

    refresh_token = create_refresh_token(
        data={
            "sub": user.username, 
        }
    )
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)
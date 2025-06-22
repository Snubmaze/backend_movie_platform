from app.auth_service.schemas import UserRead
from app.database import get_session
from app.auth_service.crud import get_user_by_username
from app.security import decode_jwt
from jose import JWTError
from fastapi import Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(
        request: Request, 
        session: AsyncSession = Depends(get_session)
    ) -> UserRead:    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_jwt(token)     
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    
    user_data = await get_user_by_username(username, session)
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead(**user_data.dict())


async def get_admin(user: UserRead = Depends(get_current_user)) -> UserRead:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return user
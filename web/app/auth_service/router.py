from app.auth_service.crud import get_user_by_username, add_user
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.auth_service.schemas import UserCreate, UserRead, TokenInfo, LoginRequest, RegisterRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.security import decode_jwt, verify_password, create_pair_jwt, create_access_token
from app.config import settings
from app.dependencies import get_current_user
from jose import JWTError


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register/", response_model=TokenInfo)
async def register(
    body: RegisterRequest, 
    session: AsyncSession = Depends(get_session)
    ):
    existing_user = await get_user_by_username(body.username, session)
    if existing_user:
        raise HTTPException(status_code=400, detail="username already taken")  

    tokens = create_pair_jwt(data={"sub": body.username})
    user_to_create = UserCreate(
        username=body.username,
        password=body.password,
        avatar_url=None
    )
    await add_user(user_to_create, session)
    return tokens


@router.post("/login", response_model=dict)
async def login(
    creds: LoginRequest, 
    response: Response, 
    session: AsyncSession = Depends(get_session)
    ):
    username = creds.username
    password = creds.password
    
    user = await get_user_by_username(username, session)
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Wrong username or password"
        )

    tokens = create_pair_jwt(data={"sub": user.username})

    response.set_cookie(
        key="access_token", 
        value=tokens.access_token,
        max_age=settings.jwt.access_token_expire_minutes * 60, 
        **settings.cookie.dict()
    )
    response.set_cookie(
        key="refresh_token", 
        value=tokens.refresh_token, 
        max_age=settings.jwt.refresh_token_expire_days * 24 * 60 * 60, 
        **settings.cookie.dict()
    )
    return tokens


@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: Request, 
    response: Response, 
    session: AsyncSession = Depends(get_session)
    ):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload  = decode_jwt(refresh_token)
        if payload.get("purpose") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        username = payload.get("sub")
        user = await get_user_by_username(username, session)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token payload")        
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
        
    new_access_token = create_access_token(data={"sub": username})

    response.set_cookie(
        key="access_token", 
        value=new_access_token,
        max_age=settings.jwt.access_token_expire_minutes * 60, 
        **settings.cookie.dict()
    )
    return {"status_code": 200, "message": "Refresh successful"}


@router.post("/logout", response_model=dict)
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"status_code": 200, "response": "Successfully logged out"}


@router.get("/me", response_model=UserRead, summary="Get current user")
async def get_me(current_user: UserRead = Depends(get_current_user)):
    return current_user
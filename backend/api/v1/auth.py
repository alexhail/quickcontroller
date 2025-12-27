from fastapi import APIRouter, Depends, HTTPException, Response, status

from api.v1.schemas import (
    MessageResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from core.config import settings
from core.deps import get_current_user, get_refresh_token
from core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from db.postgres import get_pool

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister):
    async with get_pool().acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        password_hash = hash_password(data.password)
        user = await conn.fetchrow(
            """
            INSERT INTO users (email, password_hash)
            VALUES ($1, $2)
            RETURNING id, email
            """,
            data.email,
            password_hash,
        )

    return UserResponse(id=str(user["id"]), email=user["email"])


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, response: Response):
    async with get_pool().acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, email, password_hash FROM users WHERE email = $1",
            data.email,
        )

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_id = str(user["id"])
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(response: Response, user_id: str = Depends(get_refresh_token)):
    async with get_pool().acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM users WHERE id = $1", user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    response.delete_cookie(key="refresh_token")
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(id=str(current_user["id"]), email=current_user["email"])

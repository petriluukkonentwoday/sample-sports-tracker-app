"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.auth.schemas import (
    TokenRefresh,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from src.auth.service import AuthService
from src.database import get_db
from src.database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Register a new user account."""
    service = AuthService(db)

    try:
        user = await service.register_user(data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return service.create_tokens(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Login with email and password."""
    service = AuthService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Refresh an access token using a refresh token."""
    service = AuthService(db)
    new_access_token = service.refresh_access_token(data.refresh_token)

    if new_access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    return {
        "access_token": new_access_token,
        "refresh_token": data.refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get the current authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    updates: dict[str, str],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update the current user's profile."""
    allowed_fields = {"full_name", "avatar_url", "preferred_units", "timezone"}

    for field, value in updates.items():
        if field in allowed_fields:
            setattr(current_user, field, value)

    db.add(current_user)
    return current_user

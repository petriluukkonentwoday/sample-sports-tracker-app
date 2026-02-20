"""Authentication service layer."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserRegister
from src.auth.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from src.database.models import User


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register_user(self, data: UserRegister) -> User:
        """Register a new user with email and password."""
        # Check if email already exists
        existing = await self.db.execute(
            select(User).where(User.email == data.email.lower())
        )
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()

        if user is None or user.hashed_password is None:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        return user

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get a user by their ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by their email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_or_create_oauth_user(
        self,
        provider: str,
        oauth_id: str,
        email: str,
        full_name: str,
        avatar_url: str | None = None,
    ) -> User:
        """Get or create a user from OAuth provider data."""
        # Try to find by OAuth ID first
        result = await self.db.execute(
            select(User).where(
                User.oauth_provider == provider,
                User.oauth_id == oauth_id,
            )
        )
        user = result.scalar_one_or_none()

        if user:
            return user

        # Try to find by email and link OAuth
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()

        if user:
            user.oauth_provider = provider
            user.oauth_id = oauth_id
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            return user

        # Create new user
        user = User(
            email=email.lower(),
            full_name=full_name,
            avatar_url=avatar_url,
            oauth_provider=provider,
            oauth_id=oauth_id,
            is_verified=True,  # OAuth users are pre-verified
        )
        self.db.add(user)
        await self.db.flush()
        return user

    @staticmethod
    def create_tokens(user: User) -> dict[str, str]:
        """Create access and refresh tokens for a user."""
        token_data = {"sub": user.id}
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer",
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> str | None:
        """Create a new access token from a valid refresh token."""
        payload = verify_token(refresh_token, token_type="refresh")
        if payload is None:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        return create_access_token({"sub": user_id})

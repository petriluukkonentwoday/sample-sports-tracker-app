"""Pydantic schemas for authentication."""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str


class PasswordReset(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str
    new_password: str = Field(min_length=8, max_length=100)


class OAuthCallback(BaseModel):
    """Schema for OAuth callback data."""

    provider: str
    code: str
    redirect_uri: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str
    full_name: str
    avatar_url: str | None
    preferred_units: str
    timezone: str
    is_verified: bool

    model_config = {"from_attributes": True}

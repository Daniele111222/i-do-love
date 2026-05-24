"""User and authentication schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields."""

    email: EmailStr
    nickname: str | None = None


class UserCreate(UserBase):
    """Request schema for creating users."""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Request schema for updating users."""

    nickname: str | None = None
    password: str | None = Field(None, min_length=8, max_length=128)


class UserResponse(UserBase):
    """User response schema without sensitive fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str | None = None
    exp: datetime | None = None
    type: str | None = None


class CurrentUser(BaseModel):
    """Authenticated user context passed through dependencies."""

    user_id: int
    role: str


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    nickname: str | None = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str

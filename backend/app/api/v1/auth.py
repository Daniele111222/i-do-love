"""Authentication API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_auth_service, get_current_user
from app.schemas.user import (
    CurrentUser,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    Token,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.exceptions import AuthenticationError, ConflictError, NotFoundError

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Register a new user account."""
    try:
        return await auth_service.register(
            email=request.email,
            password=request.password,
            nickname=request.nickname,
        )
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Login with email and password."""
    try:
        return await auth_service.login(email=request.email, password=request.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Issue a new access token from a refresh token."""
    try:
        return await auth_service.refresh_token(request.refresh_token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Return the current authenticated user's profile."""
    auth_service = AuthService(db)
    try:
        user = await auth_service.get_active_user_by_id(current_user.user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(user)

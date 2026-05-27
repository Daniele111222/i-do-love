"""Authentication API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import settings
from app.dependencies import get_auth_service, get_current_user
from app.schemas.user import (
    CurrentUser,
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenSessionListResponse,
    RegisterRequest,
    Token,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.services.rate_limit_service import check_rate_limit

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    request_context: Request,
    request: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Register a new user account."""
    try:
        return await auth_service.register(
            email=request.email,
            password=request.password,
            nickname=request.nickname,
            ip_address=_client_key(request_context),
            user_agent=_user_agent(request_context),
        )
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=Token)
async def login(
    request_context: Request,
    request: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Login with email and password."""
    await _enforce_rate_limit(
        key=f"auth:login:{_client_key(request_context)}:{request.email.lower()}",
        limit=settings.AUTH_LOGIN_RATE_LIMIT,
        window_seconds=settings.AUTH_RATE_LIMIT_WINDOW_SECONDS,
        message="Too many login attempts",
    )
    try:
        return await auth_service.login(
            email=request.email,
            password=request.password,
            ip_address=_client_key(request_context),
            user_agent=_user_agent(request_context),
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request_context: Request,
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """Issue a new access token from a refresh token."""
    await _enforce_rate_limit(
        key=f"auth:refresh:{_client_key(request_context)}",
        limit=settings.AUTH_REFRESH_RATE_LIMIT,
        window_seconds=settings.AUTH_RATE_LIMIT_WINDOW_SECONDS,
        message="Too many token refresh attempts",
    )
    try:
        return await auth_service.refresh_token(
            request.refresh_token,
            ip_address=_client_key(request_context),
            user_agent=_user_agent(request_context),
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """Revoke the supplied refresh token session."""
    try:
        await auth_service.logout(request.refresh_token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.get("/sessions", response_model=RefreshTokenSessionListResponse)
async def list_sessions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RefreshTokenSessionListResponse:
    """Return refresh token sessions for the current user."""
    sessions = await auth_service.list_refresh_token_sessions(
        current_user.user_id,
        current_session_id=current_user.session_id,
    )
    return RefreshTokenSessionListResponse(sessions=sessions)


@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_all_sessions(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """Revoke all refresh token sessions for the current user."""
    await auth_service.revoke_all_refresh_token_sessions(current_user.user_id)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Return the current authenticated user's profile."""
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


def _client_key(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",", maxsplit=1)[0].strip()
    if request.client is None:
        return "unknown"
    return request.client.host


def _user_agent(request: Request) -> str | None:
    user_agent = request.headers.get("User-Agent")
    if user_agent is None:
        return None
    return user_agent[:512]


async def _enforce_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
    message: str,
) -> None:
    decision = await check_rate_limit(
        key=key,
        limit=limit,
        window_seconds=window_seconds,
    )
    if decision.allowed:
        return

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=message,
        headers={"Retry-After": str(decision.retry_after_seconds)},
    )

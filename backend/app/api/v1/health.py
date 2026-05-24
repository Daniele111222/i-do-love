"""Health check API routes."""

from __future__ import annotations

from collections.abc import Awaitable
from inspect import isawaitable
from typing import Annotated, cast

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import get_db

router = APIRouter()


async def _maybe_await(value: object) -> object:
    """Await Redis methods when the installed client exposes them as awaitables."""
    if isawaitable(value):
        return await cast(Awaitable[object], value)
    return value


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


class DependencyHealthResponse(BaseModel):
    """Dependency health check response."""

    status: str
    dependency: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthResponse:
    """Check API process health."""
    return HealthResponse(status="healthy", version="0.1.0")


@router.get(
    "/health/db",
    response_model=DependencyHealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check_db(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DependencyHealthResponse:
    """Check database connectivity."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc

    return DependencyHealthResponse(status="healthy", dependency="database")


@router.get(
    "/health/redis",
    response_model=DependencyHealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check_redis() -> DependencyHealthResponse:
    """Check Redis connectivity."""
    client = redis.from_url(settings.REDIS_URL)
    try:
        await _maybe_await(client.ping())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis is unavailable",
        ) from exc
    finally:
        await _maybe_await(client.aclose())

    return DependencyHealthResponse(status="healthy", dependency="redis")

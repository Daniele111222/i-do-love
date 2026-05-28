"""Deployment readiness checks for required and optional dependencies."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from inspect import isawaitable
from typing import cast

import httpx
import redis.asyncio as redis
from sqlalchemy import text

from app.core.config import settings
from app.database import AsyncSessionLocal


@dataclass(frozen=True)
class DependencyReadiness:
    """Readiness status for a single dependency."""

    name: str
    status: str
    required: bool
    message: str | None = None


async def _maybe_await(value: object) -> object:
    """Await dependency client calls that may be sync or async across versions."""
    if isawaitable(value):
        return await cast(Awaitable[object], value)
    return value


async def check_database() -> DependencyReadiness:
    """Check database connectivity using a lightweight query."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        return DependencyReadiness(
            name="database",
            status="unavailable",
            required=True,
            message=str(exc),
        )

    return DependencyReadiness(name="database", status="ready", required=True)


async def check_redis() -> DependencyReadiness:
    """Check Redis connectivity."""
    client = redis.from_url(settings.REDIS_URL)
    try:
        await _maybe_await(client.ping())
    except Exception as exc:
        return DependencyReadiness(
            name="redis",
            status="unavailable",
            required=True,
            message=str(exc),
        )
    finally:
        await _maybe_await(client.aclose())

    return DependencyReadiness(name="redis", status="ready", required=True)


async def check_qdrant() -> DependencyReadiness:
    """Check Qdrant only when configured."""
    if not settings.QDRANT_URL:
        return DependencyReadiness(name="qdrant", status="skipped", required=False)

    url = settings.QDRANT_URL.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{url}/healthz")
            response.raise_for_status()
    except Exception as exc:
        return DependencyReadiness(
            name="qdrant",
            status="unavailable",
            required=False,
            message=str(exc),
        )

    return DependencyReadiness(name="qdrant", status="ready", required=False)


async def check_openai() -> DependencyReadiness:
    """Check OpenAI availability with a lightweight models-list request."""
    if not settings.OPENAI_API_KEY:
        return DependencyReadiness(name="openai", status="skipped", required=False)

    url = settings.OPENAI_BASE_URL.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=settings.OPENAI_HEALTH_TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{url}/models",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            )
            response.raise_for_status()
    except Exception as exc:
        return DependencyReadiness(
            name="openai",
            status="unavailable",
            required=False,
            message=str(exc),
        )

    return DependencyReadiness(name="openai", status="ready", required=False)


async def get_readiness(
    checks: tuple[Callable[[], Awaitable[DependencyReadiness]], ...] = (
        check_database,
        check_redis,
        check_qdrant,
        check_openai,
    ),
) -> list[DependencyReadiness]:
    """Run readiness checks and return each dependency's status."""
    results: list[DependencyReadiness] = []
    for check in checks:
        results.append(await check())
    return results


def is_ready(dependencies: list[DependencyReadiness]) -> bool:
    """Required dependencies must be ready for the service to receive traffic."""
    return all(
        not dependency.required or dependency.status in {"ready", "configured"}
        for dependency in dependencies
    )

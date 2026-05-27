"""Redis-backed fixed-window rate limiting."""

from __future__ import annotations

from collections.abc import Awaitable
from dataclasses import dataclass
from inspect import isawaitable
from typing import cast

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import audit_logger


@dataclass(frozen=True)
class RateLimitDecision:
    """Result of a rate limit check."""

    allowed: bool
    retry_after_seconds: int


async def _maybe_await(value: object) -> object:
    if isawaitable(value):
        return await cast(Awaitable[object], value)
    return value


def _to_int(value: object) -> int:
    if isinstance(value, int | str | bytes | bytearray):
        return int(value)
    raise TypeError(f"Expected integer-like Redis response, got {type(value).__name__}")


async def check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> RateLimitDecision:
    """Allow at most ``limit`` requests per Redis-backed fixed window."""
    client = redis.from_url(settings.REDIS_URL)
    try:
        count = _to_int(await _maybe_await(client.incr(key)))
        if count == 1:
            await _maybe_await(client.expire(key, window_seconds))

        ttl = _to_int(await _maybe_await(client.ttl(key)))
        retry_after = ttl if ttl > 0 else window_seconds
    except Exception as exc:
        audit_logger.warning("rate_limit_unavailable", extra={"key": key, "error": str(exc)})
        return RateLimitDecision(allowed=False, retry_after_seconds=window_seconds)
    finally:
        await _maybe_await(client.aclose())

    return RateLimitDecision(
        allowed=count <= limit,
        retry_after_seconds=retry_after,
    )

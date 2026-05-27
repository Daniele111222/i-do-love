"""Rate limiting service tests."""

from __future__ import annotations

import pytest

from app.services import rate_limit_service


class FakeRedis:
    """Small Redis double for fixed-window counter behavior."""

    def __init__(self) -> None:
        self.count = 0
        self.ttl_seconds = -1
        self.closed = False

    async def incr(self, key: str) -> int:
        self.count += 1
        return self.count

    async def expire(self, key: str, seconds: int) -> bool:
        self.ttl_seconds = seconds
        return True

    async def ttl(self, key: str) -> int:
        return self.ttl_seconds

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_rate_limit_denies_requests_after_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    redis_client = FakeRedis()
    monkeypatch.setattr(rate_limit_service.redis, "from_url", lambda url: redis_client)

    first = await rate_limit_service.check_rate_limit("auth:login:test", limit=2, window_seconds=60)
    second = await rate_limit_service.check_rate_limit(
        "auth:login:test",
        limit=2,
        window_seconds=60,
    )
    third = await rate_limit_service.check_rate_limit("auth:login:test", limit=2, window_seconds=60)

    assert first.allowed is True
    assert second.allowed is True
    assert third.allowed is False
    assert third.retry_after_seconds == 60
    assert redis_client.closed is True

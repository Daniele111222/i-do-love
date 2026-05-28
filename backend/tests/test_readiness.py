"""Readiness service tests."""

from __future__ import annotations

import httpx
import pytest

from app.core.config import settings
from app.services import readiness_service


@pytest.mark.asyncio
async def test_openai_readiness_checks_models_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configured OpenAI readiness performs a lightweight authenticated request."""
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "OPENAI_BASE_URL", "https://api.openai.test/v1")

    observed: dict[str, object] = {}
    real_async_client = httpx.AsyncClient

    async def handler(request: httpx.Request) -> httpx.Response:
        observed["url"] = str(request.url)
        observed["authorization"] = request.headers.get("Authorization")
        return httpx.Response(200, json={"data": []})

    monkeypatch.setattr(
        readiness_service.httpx,
        "AsyncClient",
        lambda timeout: real_async_client(
            transport=httpx.MockTransport(handler),
            timeout=timeout,
        ),
    )

    result = await readiness_service.check_openai()

    assert result.name == "openai"
    assert result.status == "ready"
    assert result.required is False
    assert observed == {
        "url": "https://api.openai.test/v1/models",
        "authorization": "Bearer test-key",
    }


@pytest.mark.asyncio
async def test_openai_readiness_reports_unavailable_on_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configured OpenAI readiness reports unavailable when the probe fails."""
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "OPENAI_BASE_URL", "https://api.openai.test/v1")
    real_async_client = httpx.AsyncClient

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": {"message": "bad key"}})

    monkeypatch.setattr(
        readiness_service.httpx,
        "AsyncClient",
        lambda timeout: real_async_client(
            transport=httpx.MockTransport(handler),
            timeout=timeout,
        ),
    )

    result = await readiness_service.check_openai()

    assert result.name == "openai"
    assert result.status == "unavailable"
    assert result.required is False
    assert result.message is not None

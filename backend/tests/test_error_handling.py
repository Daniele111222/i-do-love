"""API error handling and request ID tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_http_errors_use_stable_error_envelope(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "WrongPassword"},
    )

    assert response.status_code == 401
    assert response.headers["X-Request-ID"]
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Invalid email or password",
            "request_id": response.headers["X-Request-ID"],
        }
    }


@pytest.mark.asyncio
async def test_request_id_header_is_preserved(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health", headers={"X-Request-ID": "req-test"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test"


@pytest.mark.asyncio
async def test_validation_errors_use_stable_error_envelope(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/register", json={"email": "bad"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_http_errors_can_include_structured_details(client: AsyncClient) -> None:
    response = await client.get("/api/v1/readyz")

    if response.status_code == 200:
        pytest.skip("All required readiness dependencies are available in this environment")

    body = response.json()
    assert body["error"]["code"] == "service_unavailable"
    assert body["error"]["details"]["status"] == "not_ready"
    assert "dependencies" in body["error"]["details"]

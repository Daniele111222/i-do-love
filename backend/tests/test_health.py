"""Health API tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.api.v1 import health
from app.services.readiness_service import DependencyReadiness


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the process health check endpoint."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check_db(client: AsyncClient):
    """Test the database health check endpoint."""
    response = await client.get("/api/v1/health/db")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dependency"] == "database"


@pytest.mark.asyncio
async def test_readiness_reports_ready_when_required_dependencies_are_ready(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Readiness aggregates dependency status and skips optional unconfigured services."""

    async def fake_get_readiness() -> list[DependencyReadiness]:
        return [
            DependencyReadiness(name="database", status="ready", required=True),
            DependencyReadiness(name="redis", status="ready", required=True),
            DependencyReadiness(name="qdrant", status="skipped", required=False),
            DependencyReadiness(name="openai", status="skipped", required=False),
        ]

    monkeypatch.setattr(health, "get_readiness", fake_get_readiness)

    response = await client.get("/api/v1/readyz")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["dependencies"]["database"]["status"] == "ready"
    assert data["dependencies"]["redis"]["required"] is True
    assert data["dependencies"]["qdrant"]["status"] == "skipped"
    assert data["dependencies"]["openai"]["required"] is False


@pytest.mark.asyncio
async def test_readiness_returns_503_when_required_dependency_is_unavailable(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed required dependency makes the service not ready for traffic."""

    async def fake_get_readiness() -> list[DependencyReadiness]:
        return [
            DependencyReadiness(name="database", status="ready", required=True),
            DependencyReadiness(
                name="redis",
                status="unavailable",
                required=True,
                message="Redis is unavailable",
            ),
        ]

    monkeypatch.setattr(health, "get_readiness", fake_get_readiness)

    response = await client.get("/api/v1/readyz")

    assert response.status_code == 503
    details = response.json()["error"]["details"]
    assert details["status"] == "not_ready"
    assert details["dependencies"]["database"]["status"] == "ready"
    assert details["dependencies"]["redis"]["status"] == "unavailable"
    assert details["dependencies"]["redis"]["message"] == "Redis is unavailable"

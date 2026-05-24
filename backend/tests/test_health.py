"""Health API tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


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

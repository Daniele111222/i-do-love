"""Authentication API tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Test1234", "nickname": "TestUser"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test duplicate email registration."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "Test1234"},
    )

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "Test1234"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test user login."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "Test1234"},
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "Test1234"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with a wrong password."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "password": "Test1234"},
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPassword"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_info(client: AsyncClient):
    """Test fetching the authenticated user's profile."""
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "Test1234", "nickname": "Me"},
    )
    token = register_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["nickname"] == "Me"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test issuing a new token pair from a refresh token."""
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@example.com", "password": "Test1234"},
    )
    refresh_token = register_response.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

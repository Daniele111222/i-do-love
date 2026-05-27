"""Authentication API tests."""

from __future__ import annotations

import logging

import pytest
from httpx import AsyncClient

from app.api.v1 import auth
from app.dependencies import get_auth_service
from app.main import app
from app.schemas.user import CurrentUser
from app.services.rate_limit_service import RateLimitDecision
from app.services.exceptions import AuthenticationError


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
async def test_login_is_rate_limited(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Login rejects requests when the rate limiter denies the client."""

    async def fake_check_rate_limit(key: str, limit: int, window_seconds: int) -> RateLimitDecision:
        assert key.startswith("auth:login:")
        assert limit > 0
        assert window_seconds > 0
        return RateLimitDecision(allowed=False, retry_after_seconds=42)

    monkeypatch.setattr(auth, "check_rate_limit", fake_check_rate_limit)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "limited@example.com", "password": "Test1234"},
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "42"
    body = response.json()
    assert body["error"]["code"] == "too_many_requests"
    assert body["error"]["message"] == "Too many login attempts"


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


@pytest.mark.asyncio
async def test_refresh_token_is_rate_limited(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Refresh rejects requests when the rate limiter denies the client."""

    async def fake_check_rate_limit(key: str, limit: int, window_seconds: int) -> RateLimitDecision:
        assert key.startswith("auth:refresh:")
        assert limit > 0
        assert window_seconds > 0
        return RateLimitDecision(allowed=False, retry_after_seconds=17)

    monkeypatch.setattr(auth, "check_rate_limit", fake_check_rate_limit)

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "any-token"},
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "17"
    body = response.json()
    assert body["error"]["code"] == "too_many_requests"
    assert body["error"]["message"] == "Too many token refresh attempts"


@pytest.mark.asyncio
async def test_refresh_token_is_rotated_and_old_token_is_revoked(client: AsyncClient):
    """A refresh token can only be used once."""
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "rotate@example.com", "password": "Test1234"},
    )
    old_refresh_token = register_response.json()["refresh_token"]

    first_refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert first_refresh_response.status_code == 200
    new_refresh_token = first_refresh_response.json()["refresh_token"]
    assert new_refresh_token != old_refresh_token

    reused_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert reused_response.status_code == 401

    second_refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh_token},
    )
    assert second_refresh_response.status_code == 200


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client: AsyncClient):
    """Logout revokes the supplied refresh token session."""
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "logout@example.com", "password": "Test1234"},
    )
    refresh_token = register_response.json()["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 204

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_list_refresh_token_sessions(client: AsyncClient):
    """The current user can inspect active and revoked refresh token sessions."""
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "sessions@example.com", "password": "Test1234"},
    )
    first_tokens = register_response.json()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "sessions@example.com", "password": "Test1234"},
    )
    second_tokens = login_response.json()

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": first_tokens["refresh_token"]},
    )
    assert logout_response.status_code == 204

    response = await client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {second_tokens['access_token']}"},
    )

    assert response.status_code == 200
    sessions = response.json()["sessions"]
    assert len(sessions) == 2
    assert sessions[0]["created_at"] >= sessions[1]["created_at"]
    assert {session["is_current"] for session in sessions} == {True, False}
    assert {session["is_revoked"] for session in sessions} == {True, False}
    assert all("token_hash" not in session for session in sessions)


@pytest.mark.asyncio
async def test_refresh_token_sessions_include_request_metadata(client: AsyncClient):
    """Refresh token sessions expose safe source metadata for account review."""
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "metadata@example.com", "password": "Test1234"},
        headers={
            "User-Agent": "RegisterBrowser/1.0",
            "X-Forwarded-For": "203.0.113.10, 10.0.0.1",
        },
    )
    register_tokens = register_response.json()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "metadata@example.com", "password": "Test1234"},
        headers={
            "User-Agent": "LoginBrowser/2.0",
            "X-Forwarded-For": "198.51.100.7",
        },
    )
    login_tokens = login_response.json()

    response = await client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {login_tokens['access_token']}"},
    )

    assert response.status_code == 200
    sessions = response.json()["sessions"]
    current_session = next(session for session in sessions if session["is_current"])
    previous_session = next(session for session in sessions if not session["is_current"])

    assert current_session["ip_address"] == "198.51.100.7"
    assert current_session["user_agent"] == "LoginBrowser/2.0"
    assert previous_session["ip_address"] == "203.0.113.10"
    assert previous_session["user_agent"] == "RegisterBrowser/1.0"
    assert all("token_hash" not in session for session in sessions)
    assert register_tokens["refresh_token"] not in str(sessions)
    assert login_tokens["refresh_token"] not in str(sessions)


@pytest.mark.asyncio
async def test_revoke_all_refresh_token_sessions(client: AsyncClient):
    """A user can revoke every refresh token session for their account."""
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "revoke-all@example.com", "password": "Test1234"},
    )
    first_tokens = register_response.json()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "revoke-all@example.com", "password": "Test1234"},
    )
    second_tokens = login_response.json()

    response = await client.delete(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {second_tokens['access_token']}"},
    )

    assert response.status_code == 204

    for refresh_token in (first_tokens["refresh_token"], second_tokens["refresh_token"]):
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_auth_actions_emit_audit_logs(client: AsyncClient, caplog: pytest.LogCaptureFixture):
    """Authentication decisions emit audit logs without exposing raw tokens."""
    caplog.set_level(logging.INFO, logger="app.audit")

    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "audit@example.com", "password": "Test1234"},
    )
    refresh_token = register_response.json()["refresh_token"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "audit@example.com", "password": "Test1234"},
    )
    access_token = login_response.json()["access_token"]

    await client.post(
        "/api/v1/auth/login",
        json={"email": "audit@example.com", "password": "WrongPassword"},
    )
    await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    await client.delete(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    messages = [record.getMessage() for record in caplog.records]
    assert "auth_register_success" in messages
    assert "auth_login_success" in messages
    assert "auth_login_failed" in messages
    assert "auth_refresh_success" in messages
    assert "auth_sessions_revoked" in messages
    assert all(refresh_token not in record.getMessage() for record in caplog.records)


@pytest.mark.asyncio
async def test_get_current_user_info_uses_auth_service_dependency(client: AsyncClient) -> None:
    """The profile endpoint must reuse the injected auth service."""

    class OverrideAuthService:
        async def get_current_user_from_token(self, token: str) -> CurrentUser:
            if token != "override-token":
                raise AuthenticationError("Invalid access token")
            return CurrentUser(user_id=123, role="tester")

        async def get_active_user_by_id(self, user_id: int) -> object:
            assert user_id == 123
            return type(
                "UserStub",
                (),
                {
                    "id": 123,
                    "email": "override@example.com",
                    "nickname": "Override",
                    "is_active": True,
                    "role": "tester",
                    "created_at": "2026-05-27T00:00:00Z",
                    "updated_at": "2026-05-27T00:00:00Z",
                },
            )()

    async def override_get_auth_service() -> OverrideAuthService:
        return OverrideAuthService()

    app.dependency_overrides[get_auth_service] = override_get_auth_service
    try:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer override-token"},
        )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "override@example.com"
    assert data["role"] == "tester"

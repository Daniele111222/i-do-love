# Backend Production Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the backend from an MVP FastAPI skeleton toward a production-ready service foundation.

**Architecture:** Keep the current FastAPI + service-layer architecture. Add production-grade cross-cutting infrastructure first: environment-aware settings validation, request IDs, structured error responses, and consistent dependency injection. Defer broad domain refactors until the foundation is in place.

**Tech Stack:** FastAPI, Pydantic Settings, SQLAlchemy async, pytest-asyncio, httpx, Ruff, mypy.

---

## File Structure

- Modify `backend/app/core/config.py`: add environment enum and production secret validation.
- Create `backend/app/core/errors.py`: define stable API error response models and handlers.
- Create `backend/app/core/middleware.py`: add request ID middleware.
- Modify `backend/app/main.py`: register middleware and exception handlers.
- Modify `backend/app/api/v1/auth.py`: use the injected `AuthService` for `/auth/me`.
- Create `backend/tests/test_config.py`: verify production config fails fast for default secrets.
- Create `backend/tests/test_error_handling.py`: verify error response shape and request ID propagation.
- Modify `backend/tests/test_auth.py`: verify `/auth/me` honors `get_auth_service` dependency overrides.
- Update `backend/AGENTS.md` if the new production rules change backend guidance.

## Task 1: Config Fail-Fast

**Files:**
- Modify: `backend/app/core/config.py`
- Test: `backend/tests/test_config.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Configuration validation tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_secret_key() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(
            APP_ENV="production",
            SECRET_KEY="change-me-in-production",
            WEBHOOK_SECRET="safe-webhook-secret",
        )


def test_production_rejects_default_webhook_secret() -> None:
    with pytest.raises(ValidationError, match="WEBHOOK_SECRET"):
        Settings(
            APP_ENV="production",
            SECRET_KEY="safe-secret-key",
            WEBHOOK_SECRET="change-me-in-production",
        )


def test_development_allows_default_local_secrets() -> None:
    settings = Settings(APP_ENV="development")

    assert settings.APP_ENV == "development"
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_config.py -q`

Expected: fail because `Settings` has no production secret validation.

- [ ] **Step 3: Implement minimal config validation**

Add `APP_ENV` and a Pydantic `model_validator` that rejects default `SECRET_KEY` and `WEBHOOK_SECRET` in production.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `uv run pytest tests/test_config.py -q`

Expected: pass.

## Task 2: Request ID and Error Envelope

**Files:**
- Create: `backend/app/core/errors.py`
- Create: `backend/app/core/middleware.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_error_handling.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_error_handling.py -q`

Expected: fail because current app returns FastAPI default error bodies and no request ID header.

- [ ] **Step 3: Implement request ID middleware**

Create middleware that reads `X-Request-ID` or generates a UUID, stores it in `request.state.request_id`, and writes the same value to the response header.

- [ ] **Step 4: Implement error handlers**

Create HTTP, validation, and generic exception handlers that return `{"error": {"code", "message", "request_id"}}`.

- [ ] **Step 5: Register middleware and handlers**

Register the middleware and handlers in `backend/app/main.py`.

- [ ] **Step 6: Run tests to verify GREEN**

Run: `uv run pytest tests/test_error_handling.py -q`

Expected: pass.

## Task 3: Auth Dependency Consistency

**Files:**
- Modify: `backend/app/api/v1/auth.py`
- Modify: `backend/tests/test_auth.py`

- [ ] **Step 1: Write failing test**

Add a test proving `/auth/me` uses the `get_auth_service` dependency override for both token resolution and profile lookup.

- [ ] **Step 2: Run test to verify RED**

Run: `uv run pytest tests/test_auth.py::test_get_current_user_info_uses_auth_service_dependency -q`

Expected: fail because `/auth/me` currently constructs `AuthService(db)` manually.

- [ ] **Step 3: Implement minimal route fix**

Inject `auth_service: Annotated[AuthService, Depends(get_auth_service)]` into `/auth/me` and remove the direct `AsyncSession` dependency.

- [ ] **Step 4: Run test to verify GREEN**

Run: `uv run pytest tests/test_auth.py::test_get_current_user_info_uses_auth_service_dependency -q`

Expected: pass.

## Task 4: Alembic Migration Foundation

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`
- Create: `backend/alembic/versions/202605270001_create_users_table.py`
- Test: `backend/tests/test_migrations.py`

- [x] **Step 1: Write failing migration test**

Verify `alembic upgrade head` can create the `users` table in a temporary SQLite database.

- [x] **Step 2: Run test to verify RED**

Run: `uv run pytest tests/test_migrations.py -q`

Observed: failed because Alembic had no `script_location`.

- [x] **Step 3: Implement migration foundation**

Add Alembic config, env file, script template, and initial users-table migration.

- [x] **Step 4: Run test to verify GREEN**

Run: `uv run pytest tests/test_migrations.py -q`

Observed: passed.

## Task 5: Documentation and Full Verification

## Task 6: Refresh Token Session Persistence

**Files:**
- Create: `backend/app/models/refresh_token_session.py`
- Create: `backend/alembic/versions/202605270002_create_refresh_token_sessions_table.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/core/security.py`
- Modify: `backend/app/services/auth_service.py`
- Modify: `backend/tests/test_auth.py`
- Modify: `backend/tests/test_migrations.py`

- [x] **Step 1: Write failing refresh rotation test**

Verify that an old refresh token cannot be reused after a successful refresh.

- [x] **Step 2: Run test to verify RED**

Run: `uv run pytest tests/test_auth.py::test_refresh_token_is_rotated_and_old_token_is_revoked -q`

Observed: failed because refresh tokens were deterministic within the same second and no session state existed.

- [x] **Step 3: Implement refresh token sessions**

Add `RefreshTokenSession`, refresh token `jti`, SHA-256 token hashes, session persistence, revocation on refresh, and a migration.

- [x] **Step 4: Verify GREEN**

Run:

```bash
uv run pytest tests/test_auth.py::test_refresh_token_is_rotated_and_old_token_is_revoked -q
uv run pytest tests/test_migrations.py -q
```

Observed: both passed after making the migration SQLite-compatible.

## Task 7: Logout Revokes Refresh Token Session

**Files:**
- Modify: `backend/app/api/v1/auth.py`
- Modify: `backend/app/services/auth_service.py`
- Modify: `backend/tests/test_auth.py`

- [x] **Step 1: Write failing logout test**

Verify `POST /api/v1/auth/logout` revokes the supplied refresh token and the token can no longer be used.

- [x] **Step 2: Run test to verify RED**

Run: `uv run pytest tests/test_auth.py::test_logout_revokes_refresh_token -q`

Observed: failed with `404` because logout did not exist.

- [x] **Step 3: Implement logout**

Add `AuthService.logout()` and `POST /api/v1/auth/logout`, reusing refresh token session validation.

- [x] **Step 4: Verify GREEN**

Run: `uv run pytest tests/test_auth.py::test_logout_revokes_refresh_token -q`

Observed: passed.

## Task 8: Request ID Request Logging

**Files:**
- Create: `backend/app/core/logging.py`
- Modify: `backend/app/core/middleware.py`
- Create: `backend/tests/test_observability.py`
- Modify: `backend/AGENTS.md`

- [x] **Step 1: Write failing observability test**

Verify that a request with `X-Request-ID` emits an `app.request` log record containing `request_id`, `method`, `path`, and `status_code`.

- [x] **Step 2: Run test to verify RED**

Run: `uv run pytest tests/test_observability.py -q`

Observed: failed because no request log existed.

- [x] **Step 3: Implement request logging**

Add `app/core/logging.py` and log `request_completed` from request middleware with `request_id`, `method`, `path`, `status_code`, and `duration_ms`.

- [x] **Step 4: Verify GREEN**

Run: `uv run pytest tests/test_observability.py -q`

Observed: passed.

## Task 9: Auth Session Management and Audit Logs

**Files:**
- Modify: `backend/app/api/v1/auth.py`
- Modify: `backend/app/core/logging.py`
- Modify: `backend/app/schemas/user.py`
- Modify: `backend/app/services/auth_service.py`
- Modify: `backend/tests/test_auth.py`
- Modify: `backend/AGENTS.md`

- [x] **Step 1: Write failing auth session and audit tests**

Verify that authenticated users can list refresh token sessions, revoke all sessions, and authentication actions emit `app.audit` logs without exposing raw tokens.

- [x] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_auth.py -q`

Observed: failed because `/api/v1/auth/sessions` did not exist and `app.audit` emitted no authentication events.

- [x] **Step 3: Implement session APIs and audit logger**

Add `RefreshTokenSessionResponse`, access-token `sid` session binding, `GET /api/v1/auth/sessions`, `DELETE /api/v1/auth/sessions`, and `app.audit` events for register/login/refresh/logout/revoke-all.

- [x] **Step 4: Verify GREEN**

Run: `uv run pytest tests/test_auth.py -q`

Observed: passed.

## Task 10: Deployment Readiness Probe

**Files:**
- Modify: `backend/app/api/v1/health.py`
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/core/errors.py`
- Create: `backend/app/services/readiness_service.py`
- Modify: `backend/tests/test_health.py`
- Modify: `backend/tests/test_error_handling.py`
- Modify: `backend/.env.example`
- Modify: `backend/AGENTS.md`

- [x] **Step 1: Write failing readiness tests**

Verify that `/api/v1/readyz` returns `ready` when required dependencies are ready, returns `503` when a required dependency is unavailable, and keeps dependency details in the stable error envelope.

- [x] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_health.py tests/test_error_handling.py -q`

Observed: failed because `readiness_service` did not exist, then failed because the error envelope did not preserve structured readiness details.

- [x] **Step 3: Implement readiness service and route**

Add `DependencyReadiness`, database/Redis/Qdrant/OpenAI readiness checks, `GET /api/v1/readyz`, `QDRANT_URL`, and optional `error.details` support for structured diagnostics.

- [x] **Step 4: Verify GREEN**

Run: `uv run pytest tests/test_health.py tests/test_error_handling.py -q`

Observed: passed.

## Task 11: Auth Rate Limiting

**Files:**
- Modify: `backend/app/api/v1/auth.py`
- Modify: `backend/app/core/config.py`
- Create: `backend/app/services/rate_limit_service.py`
- Modify: `backend/tests/conftest.py`
- Modify: `backend/tests/test_auth.py`
- Create: `backend/tests/test_rate_limit.py`
- Modify: `backend/.env.example`
- Modify: `backend/AGENTS.md`

- [x] **Step 1: Write failing auth rate-limit tests**

Verify that `/api/v1/auth/login` and `/api/v1/auth/refresh` return `429` plus `Retry-After` when the limiter denies a request.

- [x] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_auth.py -q`

Observed: failed because `app.services.rate_limit_service` did not exist.

- [x] **Step 3: Implement Redis-backed fixed-window limiter**

Add `RateLimitDecision`, `check_rate_limit()`, auth limit settings, login/refresh enforcement before `AuthService`, and test fixture isolation from real Redis.

- [x] **Step 4: Verify GREEN**

Run:

```bash
uv run pytest tests/test_rate_limit.py tests/test_auth.py -q
uv run mypy app
```

Observed: passed after narrowing Redis numeric responses for mypy strict mode.

## Task 12: Production JSON Logging

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/core/logging.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_logging.py`
- Modify: `backend/.env.example`
- Modify: `backend/AGENTS.md`

- [x] **Step 1: Write failing JSON logging tests**

Verify that `JsonLogFormatter` emits single-line JSON with standard fields and preserves structured `extra`, and that production logging configuration installs the JSON formatter.

- [x] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_logging.py -q`

Observed: failed because `JsonLogFormatter` and `configure_logging` did not exist.

- [x] **Step 3: Implement production logging configuration**

Add `LOG_LEVEL`, `JsonLogFormatter`, `configure_logging()`, and app startup configuration. Keep non-production logs human-readable.

- [x] **Step 4: Verify GREEN**

Run:

```bash
uv run pytest tests/test_logging.py tests/test_observability.py -q
uv run ruff check .
uv run mypy app
```

Observed: passed.

## Task 13: Refresh Session Source Metadata

**Files:**
- Modify: `backend/app/api/v1/auth.py`
- Modify: `backend/app/models/refresh_token_session.py`
- Modify: `backend/app/schemas/user.py`
- Modify: `backend/app/services/auth_service.py`
- Create: `backend/alembic/versions/202605270003_add_refresh_session_metadata.py`
- Modify: `backend/tests/test_auth.py`
- Modify: `backend/tests/test_migrations.py`
- Modify: `backend/AGENTS.md`

- [x] **Step 1: Write failing session metadata and migration tests**

Verify that refresh token sessions expose safe IP/User-Agent source metadata, do not expose token secrets, and that Alembic creates the new columns.

- [x] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_auth.py::test_refresh_token_sessions_include_request_metadata tests/test_migrations.py -q`

Observed: failed because the session response lacked `ip_address` / `user_agent`, and the migration did not create those columns.

- [x] **Step 3: Implement metadata capture and migration**

Pass client IP/User-Agent from auth routes into `AuthService`, persist them on `RefreshTokenSession`, expose them through session list responses, and add an Alembic migration.

- [x] **Step 4: Verify GREEN**

Run:

```bash
uv run pytest tests/test_auth.py tests/test_migrations.py -q
uv run ruff check .
uv run mypy app
```

Observed: passed.

## Task 14: Ingestion Domain Persistence Foundation

**Files:**
- Create: `backend/app/models/source.py`
- Create: `backend/app/models/article.py`
- Create: `backend/app/models/ingest_job.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/app/schemas/ingest.py`
- Create: `backend/app/services/ingest_service.py`
- Modify: `backend/app/api/v1/ingest.py`
- Create: `backend/alembic/versions/202605270004_create_ingestion_tables.py`
- Modify: `backend/tests/test_ingest.py`
- Modify: `backend/tests/test_migrations.py`
- Modify: `backend/AGENTS.md`

- [x] **Step 1: Write failing ingestion persistence tests**

Verify that signed webhook requests persist Source, Article, and IngestJob rows, that repeated `source_url` payloads update the same article, and that Alembic creates the ingestion tables.

- [x] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_ingest.py tests/test_migrations.py -q`

Observed: failed because `app.models.article` and the ingestion tables did not exist.

- [x] **Step 3: Implement ingestion models, schema, service, and migration**

Add Source/Article/IngestJob models, `app/schemas/ingest.py`, `IngestService.ingest_webhook()`, webhook route persistence, and `202605270004_create_ingestion_tables.py`.

- [x] **Step 4: Verify GREEN**

Run:

```bash
uv run pytest tests/test_ingest.py tests/test_migrations.py -q
uv run ruff check .
uv run mypy app
```

Observed: passed.

## Task 15: Feed Ingestion Queue Tracking

**Files:**
- Modify: `backend/app/api/v1/ingest.py`
- Modify: `backend/app/schemas/ingest.py`
- Modify: `backend/app/services/ingest_service.py`
- Modify: `backend/tests/test_ingest.py`
- Modify: `backend/AGENTS.md`

- [x] **Step 1: Write failing feed queue/status tests**

Verify that `POST /api/v1/ingest/feed` creates a persistent `pending` IngestJob and Source, and that `GET /api/v1/ingest/status` reports counts from the database.

- [x] **Step 2: Run tests to verify RED**

Run: `uv run pytest tests/test_ingest.py -q`

Observed: failed because `/feed` returned a placeholder response with no job id and `/status` returned hard-coded zero counts.

- [x] **Step 3: Implement feed queue tracking and status aggregation**

Add `FeedIngestResponse`, `IngestService.queue_feed()`, `IngestService.get_status()`, and route wiring.

- [x] **Step 4: Verify GREEN**

Run:

```bash
uv run pytest tests/test_ingest.py -q
uv run ruff check .
uv run mypy app
```

Observed: passed after guarding the feed job source-id invariant for mypy strict mode.

**Files:**
- Modify: `backend/AGENTS.md`

- [ ] **Step 1: Update backend guidance**

Document that request ID middleware, unified error envelope, and production config fail-fast are now established rules.

- [ ] **Step 2: Run full backend verification**

Run:

```bash
uv run pytest
uv run ruff check .
uv run mypy app
```

Expected: all pass.

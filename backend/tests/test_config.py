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

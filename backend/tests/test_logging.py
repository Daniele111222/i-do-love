"""Logging configuration tests."""

from __future__ import annotations

import json
import logging

from app.core.logging import JsonLogFormatter, configure_logging


def test_json_log_formatter_preserves_standard_and_extra_fields() -> None:
    formatter = JsonLogFormatter()
    record = logging.LogRecord(
        name="app.request",
        level=logging.INFO,
        pathname=__file__,
        lineno=12,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-json"
    record.status_code = 200

    payload = json.loads(formatter.format(record))

    assert payload["timestamp"]
    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.request"
    assert payload["message"] == "request_completed"
    assert payload["request_id"] == "req-json"
    assert payload["status_code"] == 200


def test_configure_logging_uses_json_formatter_in_production() -> None:
    configure_logging(app_env="production", log_level="INFO")

    root_logger = logging.getLogger()

    assert root_logger.level == logging.INFO
    assert root_logger.handlers
    assert isinstance(root_logger.handlers[0].formatter, JsonLogFormatter)

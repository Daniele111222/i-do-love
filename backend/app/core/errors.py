"""API error response helpers."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorDetail(BaseModel):
    """Stable API error body."""

    code: str
    message: str
    request_id: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Stable API error envelope."""

    error: ErrorDetail


def get_request_id(request: Request) -> str:
    """Return the request id assigned by middleware, or a fallback marker."""
    value = getattr(request.state, "request_id", None)
    if isinstance(value, str) and value:
        return value
    return "unknown"


def _error_payload(
    code: str,
    message: str,
    request: Request,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            request_id=get_request_id(request),
            details=details,
        )
    ).model_dump(exclude_none=True)


def _status_code_to_error_code(status_code: int) -> str:
    try:
        phrase = HTTPStatus(status_code).phrase
    except ValueError:
        return "http_error"
    return phrase.lower().replace(" ", "_").replace("-", "_")


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Convert HTTP exceptions into the stable API error envelope."""
    if isinstance(exc.detail, dict):
        message = str(exc.detail.get("message", HTTPStatus(exc.status_code).phrase))
        details = exc.detail.get("details")
        if not isinstance(details, dict):
            details = None
    else:
        message = exc.detail if isinstance(exc.detail, str) else HTTPStatus(exc.status_code).phrase
        details = None

    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(
            code=_status_code_to_error_code(exc.status_code),
            message=message,
            request=request,
            details=details,
        ),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Convert request validation failures into the stable API error envelope."""
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            code="validation_error",
            message="Request validation failed",
            request=request,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Hide internal errors behind a stable 500 envelope."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload(
            code="internal_server_error",
            message="Internal server error",
            request=request,
        ),
    )

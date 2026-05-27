"""FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging
from app.core.middleware import request_id_middleware

ExceptionHandler = Callable[[Request, Exception], Response | Awaitable[Response]]

configure_logging(app_env=settings.APP_ENV, log_level=settings.LOG_LEVEL)

app = FastAPI(
    title="AI News Hub API",
    description="AI News Hub Backend API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(request_id_middleware)
app.add_exception_handler(
    StarletteHTTPException,
    cast(ExceptionHandler, http_exception_handler),
)
app.add_exception_handler(
    RequestValidationError,
    cast(ExceptionHandler, validation_exception_handler),
)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Return basic API metadata."""
    return {"message": "AI News Hub API", "version": "0.1.0"}

"""Service-layer exceptions."""

from __future__ import annotations


class ServiceError(Exception):
    """Base class for expected service-layer failures."""


class ConflictError(ServiceError):
    """Raised when a resource conflicts with existing state."""


class AuthenticationError(ServiceError):
    """Raised when credentials or tokens are invalid."""


class PermissionDeniedError(ServiceError):
    """Raised when an authenticated user lacks required access."""


class NotFoundError(ServiceError):
    """Raised when a requested resource cannot be found."""


"""
Application-level exception hierarchy.

Use cases and repositories raise these instead of raising HTTPException
directly, so business logic stays framework-agnostic. The exception
middleware (app/middleware/exception_middleware.py) is the single place
that translates these into the standardized JSON error envelope.
"""
from __future__ import annotations


class AppException(Exception):
    """Base class for all application-raised exceptions."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, error_code: str | None = None) -> None:
        self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(message)


class ValidationException(AppException):
    status_code = 400
    error_code = "VALIDATION_ERROR"


class UnauthorizedException(AppException):
    status_code = 401
    error_code = "UNAUTHORIZED"


class ForbiddenException(AppException):
    status_code = 403
    error_code = "FORBIDDEN"


class NotFoundException(AppException):
    status_code = 404
    error_code = "NOT_FOUND"


class ConflictException(AppException):
    status_code = 409
    error_code = "CONFLICT"


class UnprocessableEntityException(AppException):
    status_code = 422
    error_code = "UNPROCESSABLE_ENTITY"


class RateLimitException(AppException):
    status_code = 429
    error_code = "RATE_LIMITED"


class ServiceUnavailableException(AppException):
    status_code = 503
    error_code = "SERVICE_UNAVAILABLE"

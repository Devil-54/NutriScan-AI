from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger()


def _error_envelope(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    """
    Central place all exception -> HTTP response translation happens.
    Nothing downstream (routers, use cases) needs to know about HTTP status
    codes or the response envelope shape - they raise domain exceptions and
    this is the only place that turns them into wire format.
    """

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        logger.bind(event="APP_EXCEPTION", error_code=exc.error_code, path=request.url.path).warning(
            "Application request failed"
        )
        return JSONResponse(status_code=exc.status_code, content=_error_envelope(exc.error_code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        first_error = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(loc) for loc in first_error.get("loc", []) if loc != "body")
        message = f"{field}: {first_error.get('msg', 'Invalid input')}" if field else "Invalid input"
        safe_errors = [
            {"location": error.get("loc", ()), "type": error.get("type", "")}
            for error in exc.errors()
        ]
        logger.bind(event="VALIDATION_ERROR", path=request.url.path, errors=safe_errors).info(
            "Request validation failed"
        )
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=_error_envelope("VALIDATION_ERROR", message))

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_envelope("HTTP_ERROR", str(exc.detail)),
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.bind(event="DB_INTEGRITY_ERROR", path=request.url.path).error(
            "Database integrity constraint failed"
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_error_envelope("CONFLICT", "The request conflicts with existing data"),
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_db_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.bind(event="DB_ERROR", path=request.url.path, exception_type=type(exc).__name__).error(
            "Database request failed"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_envelope("DATABASE_ERROR", "A database error occurred"),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.bind(event="UNHANDLED_EXCEPTION", path=request.url.path, exception_type=type(exc).__name__).error(
            "Unhandled request failure"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_envelope("INTERNAL_ERROR", "An unexpected error occurred"),
        )

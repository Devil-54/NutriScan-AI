from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import correlation_id_ctx, get_logger

logger = get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Assigns a correlation_id to every request (reused from the incoming
    X-Request-ID header if present, e.g. from an upstream gateway) and logs
    method/path/status/latency in structured form."""

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        token = correlation_id_ctx.set(correlation_id)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        finally:
            correlation_id_ctx.reset(token)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.bind(
            event="API_REQUEST",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
        ).info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")

        response.headers["X-Request-ID"] = correlation_id
        return response

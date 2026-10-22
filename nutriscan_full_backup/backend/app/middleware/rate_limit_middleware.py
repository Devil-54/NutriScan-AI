"""
Rate limiting configuration using slowapi (in-memory limiter; swap the
storage backend for Redis in production via slowapi's `storage_uri`
argument once a shared Redis instance is provisioned).

Two tiers, matching Phase 2's security design: a stricter limit on
auth-related endpoints (brute-force protection) and a default limit for
everything else.
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {"code": "RATE_LIMITED", "message": "Too many requests - please try again shortly"},
        },
    )

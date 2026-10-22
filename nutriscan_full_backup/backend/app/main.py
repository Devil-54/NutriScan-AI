from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.middleware.exception_middleware import register_exception_handlers
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit_middleware import limiter, rate_limit_exceeded_handler
from app.middleware.security_headers_middleware import SecurityHeadersMiddleware

configure_logging()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.bind(event="STARTUP").info(f"{settings.PROJECT_NAME} backend starting in {settings.ENV} mode")
    yield
    logger.bind(event="SHUTDOWN").info(f"{settings.PROJECT_NAME} backend shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI-Powered Personalized Food Safety & Ingredient Analysis System - Backend Foundation (Phase 3)",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ---- Rate limiting ----
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # ---- Custom middleware (order matters: outermost added last runs first) ----
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)

    # ---- Centralized exception handling ----
    register_exception_handlers(app)

    # ---- Routes ----
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "ok", "service": settings.PROJECT_NAME}

    return app


app = create_app()

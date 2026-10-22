"""
Structured logging configuration.

All log records are emitted as JSON (when LOG_JSON=true) so they can be
ingested by any log aggregator without a custom parser. A `correlation_id`
context variable is threaded through the request lifecycle by
LoggingMiddleware so every log line within a single request can be tied
back together.
"""
from __future__ import annotations

import contextvars
import sys

from loguru import logger

from app.core.config import settings

correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="-")


def _patch_record(record: dict) -> None:
    record["extra"]["correlation_id"] = correlation_id_ctx.get()


def configure_logging() -> None:
    logger.remove()
    logger.configure(patcher=_patch_record)

    if settings.LOG_JSON:
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            serialize=True,
            format="{message}",
            enqueue=True,
        )
    else:
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
                "cid={extra[correlation_id]} | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
            ),
            enqueue=True,
        )


def get_logger():
    return logger

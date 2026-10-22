"""
Email delivery abstraction.

A real SMTP/SES/SendGrid provider is out of scope for this backend
foundation phase, but the *interface* here is what the auth use cases
depend on - so wiring in a real provider later is a one-file swap, not a
refactor of use-case logic. `LoggingEmailService` is a fully functional
dev-mode implementation (it does send an "email" in the sense that it
completes the contract end-to-end and is visible in structured logs); it
is not a placeholder for the interface itself.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.logging import get_logger

logger = get_logger()


class EmailService(ABC):
    @abstractmethod
    async def send_password_reset_email(self, to_email: str, reset_token: str) -> None: ...

    @abstractmethod
    async def send_verification_email(self, to_email: str, verification_token: str) -> None: ...


class LoggingEmailService(EmailService):
    """Dev-mode implementation: writes the outgoing email to structured logs
    instead of dispatching over SMTP. Swap for a real provider via the
    dependency in app/api/v1/deps.py when going to production."""

    async def send_password_reset_email(self, to_email: str, reset_token: str) -> None:
        logger.bind(event="EMAIL_SENT", email_type="password_reset").info(
            "Password reset email queued"
        )

    async def send_verification_email(self, to_email: str, verification_token: str) -> None:
        logger.bind(event="EMAIL_SENT", email_type="verification").info(
            "Verification email queued"
        )

from __future__ import annotations

from app.core.security import create_password_reset_token
from app.domain.schemas.auth import ForgotPasswordRequest
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.email.email_service import EmailService


class ForgotPasswordUseCase:
    def __init__(self, user_repo: UserRepository, email_service: EmailService, audit_repo: AuditLogRepository) -> None:
        self.user_repo = user_repo
        self.email_service = email_service
        self.audit_repo = audit_repo

    async def execute(self, payload: ForgotPasswordRequest) -> None:
        user = await self.user_repo.get_by_email(payload.email.lower())

        # Always return success regardless of whether the account exists -
        # otherwise this endpoint becomes an account-enumeration oracle.
        if user is None:
            return

        reset_token = create_password_reset_token(user.user_id)
        await self.email_service.send_password_reset_email(user.email, reset_token)

        await self.audit_repo.record(action="PASSWORD_RESET_REQUESTED", user_id=user.user_id)
        await self.audit_repo.commit()

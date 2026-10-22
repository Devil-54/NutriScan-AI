from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException
from app.core.security import TokenType, decode_token
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.user_repository import UserRepository


class VerifyEmailUseCase:
    """
    Per Phase 3 scope, email verification is implemented at the structural
    level: token generation (see core/security.create_email_verification_token),
    the verify endpoint, and the audit trail are wired end-to-end. Actual
    outbound email delivery goes through the same EmailService interface
    used by password reset (see infrastructure/email/email_service.py).
    """

    def __init__(self, user_repo: UserRepository, audit_repo: AuditLogRepository) -> None:
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def execute(self, token: str) -> None:
        payload = decode_token(token, expected_type=TokenType.EMAIL_VERIFICATION)
        user_id = uuid.UUID(payload["sub"])

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Account not found", error_code="USER_NOT_FOUND")

        user.is_verified = True
        await self.audit_repo.record(action="EMAIL_VERIFIED", user_id=user.user_id)
        await self.user_repo.commit()

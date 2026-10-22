from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException
from app.core.security import TokenType, decode_token, hash_password
from app.domain.schemas.auth import ResetPasswordRequest
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.repositories.user_repository import UserRepository


class ResetPasswordUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        audit_repo: AuditLogRepository,
    ) -> None:
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.audit_repo = audit_repo

    async def execute(self, payload: ResetPasswordRequest) -> None:
        token_payload = decode_token(payload.token, expected_type=TokenType.PASSWORD_RESET)
        user_id = uuid.UUID(token_payload["sub"])

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Account not found", error_code="USER_NOT_FOUND")

        user.password_hash = hash_password(payload.new_password)

        # Resetting a password invalidates every existing session as a security measure.
        await self.refresh_token_repo.revoke_all_for_user(user.user_id)

        await self.audit_repo.record(action="PASSWORD_RESET_COMPLETED", user_id=user.user_id)
        await self.user_repo.commit()

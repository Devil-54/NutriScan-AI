from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException, UnauthorizedException
from app.core.security import hash_password, verify_password
from app.domain.schemas.auth import ChangePasswordRequest
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.repositories.user_repository import UserRepository


class ChangePasswordUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        audit_repo: AuditLogRepository,
    ) -> None:
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.audit_repo = audit_repo

    async def execute(self, user_id: uuid.UUID, payload: ChangePasswordRequest) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("Account not found", error_code="USER_NOT_FOUND")

        if not verify_password(payload.current_password, user.password_hash):
            raise UnauthorizedException("Current password is incorrect", error_code="INVALID_CURRENT_PASSWORD")

        user.password_hash = hash_password(payload.new_password)

        # Changing password invalidates all other active sessions.
        await self.refresh_token_repo.revoke_all_for_user(user.user_id)

        await self.audit_repo.record(action="PASSWORD_CHANGED", user_id=user.user_id)
        await self.user_repo.commit()

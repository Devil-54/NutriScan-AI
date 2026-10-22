from __future__ import annotations

import uuid

from app.core.security import hash_refresh_token
from app.domain.schemas.auth import LogoutRequest
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.refresh_token_repository import RefreshTokenRepository


class LogoutUserUseCase:
    def __init__(self, refresh_token_repo: RefreshTokenRepository, audit_repo: AuditLogRepository) -> None:
        self.refresh_token_repo = refresh_token_repo
        self.audit_repo = audit_repo

    async def execute(self, payload: LogoutRequest, current_user_id: uuid.UUID) -> None:
        token_hash = hash_refresh_token(payload.refresh_token)
        token = await self.refresh_token_repo.get_by_hash(token_hash)

        # Idempotent: logging out with an already-invalid token is not an error.
        if token is not None and token.user_id == current_user_id and token.is_active:
            await self.refresh_token_repo.revoke(token)

        await self.audit_repo.record(action="LOGOUT", user_id=current_user_id)
        await self.refresh_token_repo.commit()

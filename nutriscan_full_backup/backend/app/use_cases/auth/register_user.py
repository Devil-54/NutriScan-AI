from __future__ import annotations

from app.core.exceptions import ConflictException
from app.core.security import hash_password
from app.domain.schemas.auth import RegisterRequest, RegisterResponse
from app.infrastructure.db.models.user import User
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.user_repository import UserRepository


class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository, audit_repo: AuditLogRepository) -> None:
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def execute(self, payload: RegisterRequest, ip_address: str | None = None) -> RegisterResponse:
        normalized_email = payload.email.lower()

        if await self.user_repo.email_exists(normalized_email):
            raise ConflictException("An account with this email already exists", error_code="EMAIL_ALREADY_EXISTS")

        user = User(
            name=payload.name,
            email=normalized_email,
            password_hash=hash_password(payload.password),
        )
        self.user_repo.add(user)
        await self.user_repo.flush()

        await self.audit_repo.record(
            action="USER_REGISTERED",
            user_id=user.user_id,
            entity_type="user",
            entity_id=str(user.user_id),
            ip_address=ip_address,
        )

        await self.user_repo.commit()

        return RegisterResponse(user_id=user.user_id, email=user.email)

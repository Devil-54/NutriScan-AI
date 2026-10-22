from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, generate_refresh_token, verify_password
from app.domain.schemas.auth import LoginRequest, TokenResponse
from app.infrastructure.db.models.refresh_token import RefreshToken
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.repositories.user_repository import UserRepository

GENERIC_LOGIN_ERROR = "Invalid email or password"


class LoginUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        audit_repo: AuditLogRepository,
    ) -> None:
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.audit_repo = audit_repo

    async def execute(
        self, payload: LoginRequest, ip_address: str | None = None, device_info: str | None = None
    ) -> TokenResponse:
        user = await self.user_repo.get_by_email(payload.email.lower())

        # Deliberately generic error for both "no such user" and "wrong password" -
        # never reveal which one it was, to avoid leaking account existence.
        if user is None or not verify_password(payload.password, user.password_hash):
            await self.audit_repo.record(
                action="LOGIN_FAILED",
                metadata={"email": payload.email.lower()},
                ip_address=ip_address,
            )
            await self.audit_repo.commit()
            raise UnauthorizedException(GENERIC_LOGIN_ERROR, error_code="INVALID_CREDENTIALS")

        if not user.is_active:
            raise UnauthorizedException("This account has been deactivated", error_code="ACCOUNT_INACTIVE")

        access_token = create_access_token(user.user_id, role=user.role.value)
        raw_refresh_token, token_hash, expires_at = generate_refresh_token()

        refresh_token_row = RefreshToken(
            user_id=user.user_id,
            token_hash=token_hash,
            device_info=device_info,
            expires_at=expires_at,
        )
        self.refresh_token_repo.add(refresh_token_row)

        await self.audit_repo.record(
            action="LOGIN_SUCCESS",
            user_id=user.user_id,
            ip_address=ip_address,
        )

        await self.user_repo.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

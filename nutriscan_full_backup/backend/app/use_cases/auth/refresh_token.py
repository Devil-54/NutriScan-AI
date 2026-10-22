from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, generate_refresh_token, hash_refresh_token
from app.domain.schemas.auth import RefreshRequest, TokenResponse
from app.infrastructure.db.models.refresh_token import RefreshToken
from app.infrastructure.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.repositories.user_repository import UserRepository


class RefreshTokenUseCase:
    """
    Implements refresh-token rotation: every use of a refresh token revokes
    it and issues a brand new one. If a revoked/expired token is presented
    again, that is treated as a signal of potential token theft and all of
    that user's sessions are revoked as a precaution.
    """

    def __init__(self, user_repo: UserRepository, refresh_token_repo: RefreshTokenRepository) -> None:
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

    async def execute(self, payload: RefreshRequest, device_info: str | None = None) -> TokenResponse:
        token_hash = hash_refresh_token(payload.refresh_token)
        existing = await self.refresh_token_repo.get_by_hash(token_hash)

        if existing is None:
            raise UnauthorizedException("Invalid refresh token", error_code="INVALID_REFRESH_TOKEN")

        if not RefreshTokenRepository.is_valid(existing):
            # Reuse of a revoked/expired token - revoke everything for this user.
            await self.refresh_token_repo.revoke_all_for_user(existing.user_id)
            await self.refresh_token_repo.commit()
            raise UnauthorizedException(
                "Refresh token is no longer valid - please log in again", error_code="REFRESH_TOKEN_REUSED"
            )

        user = await self.user_repo.get_by_id(existing.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedException("Account is not available", error_code="ACCOUNT_INACTIVE")

        await self.refresh_token_repo.revoke(existing)

        new_access_token = create_access_token(user.user_id, role=user.role.value)
        raw_refresh_token, new_hash, expires_at = generate_refresh_token()

        new_token_row = RefreshToken(
            user_id=user.user_id,
            token_hash=new_hash,
            device_info=device_info,
            expires_at=expires_at,
        )
        self.refresh_token_repo.add(new_token_row)
        await self.refresh_token_repo.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=raw_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

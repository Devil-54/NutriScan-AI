from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.v1.deps import (
    CurrentUserDep,
    get_audit_log_repository,
    get_client_ip,
    get_device_info,
    get_email_service,
    get_refresh_token_repository,
    get_user_repository,
)
from app.core.config import settings
from app.middleware.rate_limit_middleware import limiter
from app.domain.schemas.auth import (
    ChangePasswordRequest,
    EmailVerificationRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    TokenResponse,
)
from app.domain.schemas.common import SuccessResponse
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.email.email_service import EmailService
from app.use_cases.auth.change_password import ChangePasswordUseCase
from app.use_cases.auth.forgot_password import ForgotPasswordUseCase
from app.use_cases.auth.login_user import LoginUserUseCase
from app.use_cases.auth.logout_user import LogoutUserUseCase
from app.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.use_cases.auth.register_user import RegisterUserUseCase
from app.use_cases.auth.reset_password import ResetPasswordUseCase
from app.use_cases.auth.verify_email import VerifyEmailUseCase

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=SuccessResponse[RegisterResponse], status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register(
    payload: RegisterRequest,
    request: Request,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> SuccessResponse[RegisterResponse]:
    use_case = RegisterUserUseCase(user_repo, audit_repo)
    result = await use_case.execute(payload, ip_address=get_client_ip(request))
    return SuccessResponse(data=result)


@router.post("/login", response_model=SuccessResponse[TokenResponse])
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    payload: LoginRequest,
    request: Request,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> SuccessResponse[TokenResponse]:
    use_case = LoginUserUseCase(user_repo, refresh_token_repo, audit_repo)
    result = await use_case.execute(
        payload, ip_address=get_client_ip(request), device_info=get_device_info(request)
    )
    return SuccessResponse(data=result)


@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
async def refresh(
    payload: RefreshRequest,
    request: Request,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
) -> SuccessResponse[TokenResponse]:
    use_case = RefreshTokenUseCase(user_repo, refresh_token_repo)
    result = await use_case.execute(payload, device_info=get_device_info(request))
    return SuccessResponse(data=result)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def logout(
    payload: LogoutRequest,
    current_user: CurrentUserDep,
    refresh_token_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> None:
    use_case = LogoutUserUseCase(refresh_token_repo, audit_repo)
    await use_case.execute(payload, current_user_id=current_user.user_id)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def forgot_password(
    payload: ForgotPasswordRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> None:
    use_case = ForgotPasswordUseCase(user_repo, email_service, audit_repo)
    await use_case.execute(payload)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def reset_password(
    payload: ResetPasswordRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> None:
    use_case = ResetPasswordUseCase(user_repo, refresh_token_repo, audit_repo)
    await use_case.execute(payload)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUserDep,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> None:
    use_case = ChangePasswordUseCase(user_repo, refresh_token_repo, audit_repo)
    await use_case.execute(current_user.user_id, payload)


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def verify_email(
    payload: EmailVerificationRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> None:
    use_case = VerifyEmailUseCase(user_repo, audit_repo)
    await use_case.execute(payload.token)

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps import CurrentUserDep, get_audit_log_repository, get_health_profile_repository
from app.domain.schemas.common import SuccessResponse
from app.domain.schemas.profile import (
    AllergiesUpdateRequest,
    AllergyItem,
    ConditionItem,
    ConditionsUpdateRequest,
    FullProfileRead,
    HealthProfileRead,
    HealthProfileUpdate,
)
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository
from app.use_cases.profile.get_profile import GetProfileUseCase
from app.use_cases.profile.update_allergies import UpdateAllergiesUseCase
from app.use_cases.profile.update_conditions import UpdateConditionsUseCase
from app.use_cases.profile.update_profile import UpdateProfileUseCase

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get("/me", response_model=SuccessResponse[FullProfileRead])
async def get_my_profile(
    current_user: CurrentUserDep,
    health_profile_repo: Annotated[HealthProfileRepository, Depends(get_health_profile_repository)],
) -> SuccessResponse[FullProfileRead]:
    use_case = GetProfileUseCase(health_profile_repo)
    result = await use_case.execute(current_user.user_id)
    return SuccessResponse(data=result)


@router.put("/me", response_model=SuccessResponse[HealthProfileRead])
async def update_my_profile(
    payload: HealthProfileUpdate,
    current_user: CurrentUserDep,
    health_profile_repo: Annotated[HealthProfileRepository, Depends(get_health_profile_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> SuccessResponse[HealthProfileRead]:
    use_case = UpdateProfileUseCase(health_profile_repo, audit_repo)
    result = await use_case.execute(current_user.user_id, payload)
    return SuccessResponse(data=result)


@router.put("/me/allergies", response_model=SuccessResponse[list[AllergyItem]])
async def update_my_allergies(
    payload: AllergiesUpdateRequest,
    current_user: CurrentUserDep,
    health_profile_repo: Annotated[HealthProfileRepository, Depends(get_health_profile_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> SuccessResponse[list[AllergyItem]]:
    use_case = UpdateAllergiesUseCase(health_profile_repo, audit_repo)
    result = await use_case.execute(current_user.user_id, payload)
    return SuccessResponse(data=result)


@router.put("/me/conditions", response_model=SuccessResponse[list[ConditionItem]])
async def update_my_conditions(
    payload: ConditionsUpdateRequest,
    current_user: CurrentUserDep,
    health_profile_repo: Annotated[HealthProfileRepository, Depends(get_health_profile_repository)],
    audit_repo: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> SuccessResponse[list[ConditionItem]]:
    use_case = UpdateConditionsUseCase(health_profile_repo, audit_repo)
    result = await use_case.execute(current_user.user_id, payload)
    return SuccessResponse(data=result)

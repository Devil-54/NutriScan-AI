from __future__ import annotations

import uuid

from app.core.exceptions import ValidationException
from app.domain.schemas.profile import ConditionItem, ConditionsUpdateRequest
from app.infrastructure.db.models.medical_condition import UserMedicalCondition
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository


class UpdateConditionsUseCase:
    def __init__(self, health_profile_repo: HealthProfileRepository, audit_repo: AuditLogRepository) -> None:
        self.health_profile_repo = health_profile_repo
        self.audit_repo = audit_repo

    async def execute(self, user_id: uuid.UUID, payload: ConditionsUpdateRequest) -> list[ConditionItem]:
        requested_ids = [item.condition_id for item in payload.conditions]
        existing_ids = await self.health_profile_repo.condition_ids_exist(requested_ids)

        unknown_ids = set(requested_ids) - existing_ids
        if unknown_ids:
            raise ValidationException(
                f"Unknown medical condition id(s): {', '.join(str(i) for i in unknown_ids)}",
                error_code="UNKNOWN_CONDITION",
            )

        rows = [
            UserMedicalCondition(
                user_id=user_id,
                condition_id=item.condition_id,
                severity=item.severity,
                notes=item.notes,
                diagnosed_at=item.diagnosed_at,
            )
            for item in payload.conditions
        ]
        await self.health_profile_repo.replace_conditions(user_id, rows)

        await self.audit_repo.record(
            action="MEDICAL_CONDITIONS_UPDATED",
            user_id=user_id,
            entity_type="user_medical_conditions",
            metadata={"count": len(rows)},
        )
        await self.health_profile_repo.commit()

        return payload.conditions

from __future__ import annotations

import uuid

from app.core.exceptions import ValidationException
from app.domain.schemas.profile import AllergiesUpdateRequest, AllergyItem
from app.infrastructure.db.models.allergen import UserAllergy
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository


class UpdateAllergiesUseCase:
    def __init__(self, health_profile_repo: HealthProfileRepository, audit_repo: AuditLogRepository) -> None:
        self.health_profile_repo = health_profile_repo
        self.audit_repo = audit_repo

    async def execute(self, user_id: uuid.UUID, payload: AllergiesUpdateRequest) -> list[AllergyItem]:
        requested_ids = [item.allergen_id for item in payload.allergies]
        existing_ids = await self.health_profile_repo.allergen_ids_exist(requested_ids)

        unknown_ids = set(requested_ids) - existing_ids
        if unknown_ids:
            raise ValidationException(
                f"Unknown allergen id(s): {', '.join(str(i) for i in unknown_ids)}",
                error_code="UNKNOWN_ALLERGEN",
            )

        rows = [
            UserAllergy(user_id=user_id, allergen_id=item.allergen_id, severity=item.severity)
            for item in payload.allergies
        ]
        await self.health_profile_repo.replace_allergies(user_id, rows)

        await self.audit_repo.record(
            action="ALLERGIES_UPDATED", user_id=user_id, entity_type="user_allergies", metadata={"count": len(rows)}
        )
        await self.health_profile_repo.commit()

        return payload.allergies

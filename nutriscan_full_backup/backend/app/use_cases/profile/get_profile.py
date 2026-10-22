from __future__ import annotations

import uuid

from app.domain.schemas.profile import AllergyItem, ConditionItem, FullProfileRead, HealthProfileRead
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository


class GetProfileUseCase:
    def __init__(self, health_profile_repo: HealthProfileRepository) -> None:
        self.health_profile_repo = health_profile_repo

    async def execute(self, user_id: uuid.UUID) -> FullProfileRead:
        profile = await self.health_profile_repo.get_by_user_id(user_id)
        allergies = await self.health_profile_repo.get_allergies(user_id)
        conditions = await self.health_profile_repo.get_conditions(user_id)

        return FullProfileRead(
            health_profile=HealthProfileRead.model_validate(profile) if profile else None,
            allergies=[AllergyItem(allergen_id=a.allergen_id, severity=a.severity) for a in allergies],
            conditions=[
                ConditionItem(
                    condition_id=c.condition_id,
                    severity=c.severity,
                    notes=c.notes,
                    diagnosed_at=c.diagnosed_at,
                )
                for c in conditions
            ],
        )

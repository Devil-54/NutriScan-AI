from __future__ import annotations

import uuid

from app.domain.schemas.profile import HealthProfileRead, HealthProfileUpdate
from app.infrastructure.db.models.health_profile import HealthProfile
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository


class UpdateProfileUseCase:
    def __init__(self, health_profile_repo: HealthProfileRepository, audit_repo: AuditLogRepository) -> None:
        self.health_profile_repo = health_profile_repo
        self.audit_repo = audit_repo

    async def execute(self, user_id: uuid.UUID, payload: HealthProfileUpdate) -> HealthProfileRead:
        bmi = HealthProfile.compute_bmi(payload.height_cm, payload.weight_kg)

        profile = await self.health_profile_repo.get_by_user_id(user_id)

        if profile is None:
            profile = HealthProfile(
                user_id=user_id,
                age=payload.age,
                gender=payload.gender,
                height_cm=payload.height_cm,
                weight_kg=payload.weight_kg,
                bmi=bmi,
                activity_level=payload.activity_level,
                fitness_goal=payload.fitness_goal,
                diet_preference=payload.diet_preference,
                pregnancy_status=payload.pregnancy_status,
                period_status=payload.period_status,
                allergies=payload.allergies,
                diseases=payload.diseases,
                emergency_notes=payload.emergency_notes,
            )
            self.health_profile_repo.add(profile)
            action = "HEALTH_PROFILE_CREATED"
        else:
            profile.age = payload.age
            profile.gender = payload.gender
            profile.height_cm = payload.height_cm
            profile.weight_kg = payload.weight_kg
            profile.bmi = bmi
            profile.activity_level = payload.activity_level
            profile.fitness_goal = payload.fitness_goal
            profile.diet_preference = payload.diet_preference
            profile.pregnancy_status = payload.pregnancy_status
            profile.period_status = payload.period_status
            profile.allergies = payload.allergies
            profile.diseases = payload.diseases
            profile.emergency_notes = payload.emergency_notes
            action = "HEALTH_PROFILE_UPDATED"

        await self.health_profile_repo.flush()
        await self.audit_repo.record(action=action, user_id=user_id, entity_type="health_profile")
        await self.health_profile_repo.commit()
        await self.health_profile_repo.refresh(profile)

        return HealthProfileRead.model_validate(profile)

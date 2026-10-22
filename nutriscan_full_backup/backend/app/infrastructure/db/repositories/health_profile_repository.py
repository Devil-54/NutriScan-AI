from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.allergen import Allergen, UserAllergy
from app.infrastructure.db.models.health_profile import HealthProfile
from app.infrastructure.db.models.medical_condition import MedicalCondition, UserMedicalCondition
from app.infrastructure.db.repositories.base_repository import BaseRepository


class HealthProfileRepository(BaseRepository[HealthProfile]):
    model = HealthProfile

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> HealthProfile | None:
        result = await self.session.execute(select(HealthProfile).where(HealthProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_allergies(self, user_id: uuid.UUID) -> list[UserAllergy]:
        result = await self.session.execute(select(UserAllergy).where(UserAllergy.user_id == user_id))
        return list(result.scalars().all())

    async def replace_allergies(self, user_id: uuid.UUID, items: list[UserAllergy]) -> None:
        await self.session.execute(delete(UserAllergy).where(UserAllergy.user_id == user_id))
        for item in items:
            self.session.add(item)
        await self.flush()

    async def get_conditions(self, user_id: uuid.UUID) -> list[UserMedicalCondition]:
        result = await self.session.execute(
            select(UserMedicalCondition).where(UserMedicalCondition.user_id == user_id)
        )
        return list(result.scalars().all())

    async def replace_conditions(self, user_id: uuid.UUID, items: list[UserMedicalCondition]) -> None:
        await self.session.execute(delete(UserMedicalCondition).where(UserMedicalCondition.user_id == user_id))
        for item in items:
            self.session.add(item)
        await self.flush()

    async def allergen_ids_exist(self, allergen_ids: list[uuid.UUID]) -> set[uuid.UUID]:
        if not allergen_ids:
            return set()
        result = await self.session.execute(select(Allergen.allergen_id).where(Allergen.allergen_id.in_(allergen_ids)))
        return set(result.scalars().all())

    async def condition_ids_exist(self, condition_ids: list[uuid.UUID]) -> set[uuid.UUID]:
        if not condition_ids:
            return set()
        result = await self.session.execute(
            select(MedicalCondition.condition_id).where(MedicalCondition.condition_id.in_(condition_ids))
        )
        return set(result.scalars().all())

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.ingredient_nutrition import IngredientNutrition
from app.infrastructure.db.repositories.base_repository import BaseRepository


class NutritionRepository(BaseRepository[IngredientNutrition]):
    model = IngredientNutrition

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_ingredient_id(self, ingredient_id: uuid.UUID) -> IngredientNutrition | None:
        result = await self.session.execute(
            select(IngredientNutrition).where(IngredientNutrition.ingredient_id == ingredient_id)
        )
        return result.scalar_one_or_none()

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.allergen import Allergen
from app.infrastructure.db.models.ingredient_allergen import IngredientAllergen
from app.infrastructure.db.repositories.base_repository import BaseRepository


class AllergenRepository(BaseRepository[Allergen]):
    model = Allergen

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def search(self, query: str, limit: int = 20) -> list[Allergen]:
        pattern = f"%{query}%"
        result = await self.session.execute(select(Allergen).where(Allergen.name.ilike(pattern)).limit(limit))
        return list(result.scalars().all())

    async def link_ingredient(
        self, ingredient_id: uuid.UUID, allergen_id: uuid.UUID, relationship_type: str = "contains"
    ) -> IngredientAllergen:
        link = IngredientAllergen(ingredient_id=ingredient_id, allergen_id=allergen_id, relationship_type=relationship_type)
        self.session.add(link)
        await self.flush()
        return link

    async def get_allergens_for_ingredient(self, ingredient_id: uuid.UUID) -> list[Allergen]:
        result = await self.session.execute(
            select(Allergen)
            .join(IngredientAllergen, IngredientAllergen.allergen_id == Allergen.allergen_id)
            .where(IngredientAllergen.ingredient_id == ingredient_id)
        )
        return list(result.scalars().all())

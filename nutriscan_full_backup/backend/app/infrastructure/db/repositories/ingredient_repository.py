from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models.ingredient import Ingredient, IngredientAlias
from app.infrastructure.db.repositories.base_repository import BaseRepository


class IngredientRepository(BaseRepository[Ingredient]):
    model = Ingredient

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_canonical_name(self, name: str) -> Ingredient | None:
        result = await self.session.execute(select(Ingredient).where(Ingredient.canonical_name == name))
        return result.scalar_one_or_none()

    async def get_by_source_external_id(self, source: str, external_id: str) -> Ingredient | None:
        result = await self.session.execute(
            select(Ingredient).where(Ingredient.source == source, Ingredient.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def get_with_aliases(self, ingredient_id: uuid.UUID) -> Ingredient | None:
        result = await self.session.execute(
            select(Ingredient).options(selectinload(Ingredient.aliases)).where(Ingredient.ingredient_id == ingredient_id)
        )
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 20) -> list[Ingredient]:
        pattern = f"%{query}%"
        result = await self.session.execute(
            select(Ingredient).where(Ingredient.canonical_name.ilike(pattern)).limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_alias(self, query: str, limit: int = 20) -> list[Ingredient]:
        """Resolves a raw alias/synonym search term to canonical ingredients that have a matching alias."""
        pattern = f"%{query}%"
        result = await self.session.execute(
            select(Ingredient)
            .join(IngredientAlias, IngredientAlias.ingredient_id == Ingredient.ingredient_id)
            .where(or_(IngredientAlias.alias_text.ilike(pattern), Ingredient.canonical_name.ilike(pattern)))
            .limit(limit)
        )
        return list(result.scalars().unique().all())

    async def add_alias(self, ingredient_id: uuid.UUID, alias_text: str, alias_type: str = "common_name") -> IngredientAlias:
        alias = IngredientAlias(ingredient_id=ingredient_id, alias_text=alias_text, alias_type=alias_type)
        self.session.add(alias)
        await self.flush()
        return alias

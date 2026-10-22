from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.ingredient_parse import IngredientParse
from app.infrastructure.db.repositories.base_repository import BaseRepository


class IngredientParseRepository(BaseRepository[IngredientParse]):
    model = IngredientParse

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

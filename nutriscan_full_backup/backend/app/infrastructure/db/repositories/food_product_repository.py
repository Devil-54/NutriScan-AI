from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.food_product import FoodProduct
from app.infrastructure.db.repositories.base_repository import BaseRepository


class FoodProductRepository(BaseRepository[FoodProduct]):
    model = FoodProduct

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_source_external_id(self, source: str, external_id: str) -> FoodProduct | None:
        result = await self.session.execute(
            select(FoodProduct).where(FoodProduct.source == source, FoodProduct.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 20) -> list[FoodProduct]:
        pattern = f"%{query}%"
        result = await self.session.execute(
            select(FoodProduct).where(
                (FoodProduct.name.ilike(pattern)) | (FoodProduct.brand.ilike(pattern)) | (FoodProduct.barcode == query)
            ).limit(limit)
        )
        return list(result.scalars().all())

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.additive import Additive
from app.infrastructure.db.repositories.base_repository import BaseRepository


class AdditiveRepository(BaseRepository[Additive]):
    model = Additive

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_ins_code(self, ins_code: str) -> Additive | None:
        result = await self.session.execute(select(Additive).where(Additive.ins_code == ins_code))
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 20) -> list[Additive]:
        pattern = f"%{query}%"
        result = await self.session.execute(
            select(Additive).where((Additive.ins_code.ilike(pattern)) | (Additive.common_name.ilike(pattern))).limit(limit)
        )
        return list(result.scalars().all())

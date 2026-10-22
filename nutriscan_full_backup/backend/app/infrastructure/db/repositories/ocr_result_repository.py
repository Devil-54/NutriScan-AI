from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.ocr_result import OcrResult
from app.infrastructure.db.repositories.base_repository import BaseRepository


class OcrResultRepository(BaseRepository[OcrResult]):
    model = OcrResult

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_scan_id(self, scan_id: uuid.UUID) -> OcrResult | None:
        result = await self.session.execute(select(OcrResult).where(OcrResult.scan_id == scan_id))
        return result.scalar_one_or_none()

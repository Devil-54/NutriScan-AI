from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.import_job import ImportJob
from app.infrastructure.db.repositories.base_repository import BaseRepository


class ImportJobRepository(BaseRepository[ImportJob]):
    model = ImportJob

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

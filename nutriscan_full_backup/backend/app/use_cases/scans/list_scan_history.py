from __future__ import annotations

import uuid

from app.domain.enums import ScanStatus
from app.domain.schemas.common import PaginationMeta
from app.infrastructure.db.repositories.scan_repository import ScanRepository


class ListScanHistoryUseCase:
    def __init__(self, scan_repo: ScanRepository) -> None:
        self.scan_repo = scan_repo

    async def execute(
        self,
        user_id: uuid.UUID,
        page: int,
        limit: int,
        status: ScanStatus | None,
        search: str | None,
        sort_by: str,
        sort_dir: str,
    ) -> tuple[list, PaginationMeta]:
        rows, total = await self.scan_repo.list_history(
            user_id=user_id,
            page=page,
            limit=limit,
            status=status,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        total_pages = (total + limit - 1) // limit if total else 0
        meta = PaginationMeta(page=page, limit=limit, total=total, total_pages=total_pages)
        # Return the loaded ORM rows so the API can serialize the joined,
        # immutable personalized evaluation without triggering another query.
        return rows, meta

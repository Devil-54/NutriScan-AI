from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException
from app.infrastructure.db.repositories.scan_repository import ScanRepository


class GetScanDetailUseCase:
    def __init__(self, scan_repo: ScanRepository) -> None:
        self.scan_repo = scan_repo

    async def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID):
        scan = await self.scan_repo.get_owned_by_id(scan_id, user_id, include_deleted=True)
        if scan is None:
            raise NotFoundException("Scan not found", error_code="SCAN_NOT_FOUND")

        return scan

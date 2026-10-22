from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException
from app.domain.schemas.scan import ScanStatusRead
from app.infrastructure.db.repositories.scan_repository import ScanRepository


class GetScanStatusUseCase:
    def __init__(self, scan_repo: ScanRepository) -> None:
        self.scan_repo = scan_repo

    async def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID) -> ScanStatusRead:
        scan = await self.scan_repo.get_owned_by_id(scan_id, user_id)
        if scan is None:
            raise NotFoundException("Scan not found", error_code="SCAN_NOT_FOUND")

        return ScanStatusRead(
            scan_id=scan.scan_id,
            status=scan.status,
            processing_stage=scan.processing_stage,
            retry_count=scan.retry_count,
            error_message=scan.error_message,
        )

from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException
from app.domain.schemas.scan import ScanRead, ScanUpdateRequest
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository


class UpdateScanMetadataUseCase:
    def __init__(self, scan_repo: ScanRepository, audit_repo: AuditLogRepository) -> None:
        self.scan_repo = scan_repo
        self.audit_repo = audit_repo

    async def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID, payload: ScanUpdateRequest) -> ScanRead:
        scan = await self.scan_repo.get_owned_by_id(scan_id, user_id)
        if scan is None:
            raise NotFoundException("Scan not found", error_code="SCAN_NOT_FOUND")

        scan.notes = payload.notes
        await self.scan_repo.flush()

        await self.audit_repo.record(
            action="SCAN_METADATA_UPDATED", user_id=user_id, entity_type="scan", entity_id=str(scan_id)
        )
        await self.scan_repo.commit()
        await self.scan_repo.refresh(scan)

        return ScanRead.model_validate(scan)

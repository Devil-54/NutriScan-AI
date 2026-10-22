from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository


class DeleteScanUseCase:
    """
    Soft delete: marks the row deleted and keeps the underlying files in
    place for `DELETED_SCAN_RETENTION_DAYS` so `RestoreScanUseCase` can
    bring it back. Permanent file removal happens via the expiration/cleanup
    maintenance path (see use_cases/scans/cleanup_expired_scans.py), not here.
    """

    def __init__(self, scan_repo: ScanRepository, audit_repo: AuditLogRepository) -> None:
        self.scan_repo = scan_repo
        self.audit_repo = audit_repo

    async def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID) -> None:
        scan = await self.scan_repo.get_owned_by_id(scan_id, user_id)
        if scan is None:
            raise NotFoundException("Scan not found", error_code="SCAN_NOT_FOUND")

        await self.scan_repo.soft_delete(scan)
        await self.audit_repo.record(
            action="SCAN_DELETED", user_id=user_id, entity_type="scan", entity_id=str(scan_id)
        )
        await self.scan_repo.commit()

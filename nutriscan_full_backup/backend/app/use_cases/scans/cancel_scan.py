from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException, ValidationException
from app.domain.enums import ScanStatus
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository

_CANCELLABLE_STATUSES = {ScanStatus.UPLOADED, ScanStatus.QUEUED, ScanStatus.PROCESSING}


class CancelScanUseCase:
    """
    Cancellation only makes sense before a scan reaches a terminal state.
    Phase 3B only ever produces UPLOADED scans, but this guard is written
    against the full status set now so the OCR/Analysis phases that
    introduce QUEUED/PROCESSING don't need to touch this use case.
    """

    def __init__(self, scan_repo: ScanRepository, audit_repo: AuditLogRepository) -> None:
        self.scan_repo = scan_repo
        self.audit_repo = audit_repo

    async def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID) -> None:
        scan = await self.scan_repo.get_owned_by_id(scan_id, user_id)
        if scan is None:
            raise NotFoundException("Scan not found", error_code="SCAN_NOT_FOUND")

        if scan.status not in _CANCELLABLE_STATUSES:
            raise ValidationException(
                f"Scan in status '{scan.status.value}' cannot be cancelled", error_code="INVALID_SCAN_STATE"
            )

        scan.status = ScanStatus.CANCELLED
        await self.scan_repo.flush()

        await self.audit_repo.record(
            action="SCAN_CANCELLED", user_id=user_id, entity_type="scan", entity_id=str(scan_id)
        )
        await self.scan_repo.commit()

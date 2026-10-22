from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException
from app.domain.enums import OcrStatus
from app.domain.schemas.ocr import OcrStatusResponse
from app.infrastructure.db.repositories.ocr_result_repository import OcrResultRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository


class GetOcrStatusUseCase:
    def __init__(self, scan_repo: ScanRepository, ocr_result_repo: OcrResultRepository) -> None:
        self.scan_repo = scan_repo
        self.ocr_result_repo = ocr_result_repo

    async def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID) -> OcrStatusResponse:
        scan = await self.scan_repo.get_owned_by_id(scan_id, user_id)
        if scan is None:
            raise NotFoundException("Scan not found", error_code="SCAN_NOT_FOUND")

        ocr_row = await self.ocr_result_repo.get_by_scan_id(scan_id)
        status = ocr_row.status if ocr_row else OcrStatus.PENDING
        processing_time_ms = ocr_row.processing_time_ms if ocr_row else None

        return OcrStatusResponse(scan_id=scan_id, status=status, processing_time_ms=processing_time_ms)

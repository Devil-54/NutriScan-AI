from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException, ValidationException
from app.domain.enums import OcrStatus
from app.domain.schemas.ocr import OcrResultResponse
from app.infrastructure.db.repositories.ocr_result_repository import OcrResultRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.ocr.label_extraction import extract_label_data


class GetOcrResultUseCase:
    def __init__(self, scan_repo: ScanRepository, ocr_result_repo: OcrResultRepository) -> None:
        self.scan_repo = scan_repo
        self.ocr_result_repo = ocr_result_repo

    async def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID) -> OcrResultResponse:
        scan = await self.scan_repo.get_owned_by_id(scan_id, user_id)
        if scan is None:
            raise NotFoundException("Scan not found", error_code="SCAN_NOT_FOUND")

        ocr_row = await self.ocr_result_repo.get_by_scan_id(scan_id)
        if ocr_row is None or ocr_row.status != OcrStatus.COMPLETED:
            raise ValidationException("OCR result not available for this scan", error_code="OCR_NOT_READY")

        metadata = ocr_row.bounding_boxes if isinstance(ocr_row.bounding_boxes, dict) else {}
        label = extract_label_data(str(metadata.get("raw_text") or ocr_row.ingredients_text or ""))
        return OcrResultResponse(
            ingredients_text=label.ingredients_text,
            confidence=ocr_row.confidence or 0.0,
            engine=ocr_row.engine,
            product_name=metadata.get("product_name") or label.product_name,
            brand=metadata.get("brand") or label.brand,
            category=metadata.get("category") or label.category,
            nutrition=metadata.get("nutrition") or label.nutrition,
        )

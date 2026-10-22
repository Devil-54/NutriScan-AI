from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundException, ValidationException
from app.core.logging import get_logger
from app.domain.enums import OcrStatus, ProcessingStage, ScanStatus
from app.domain.schemas.ocr import OcrProcessResponse
from app.infrastructure.db.models.ocr_result import OcrResult
from app.infrastructure.db.repositories.ocr_result_repository import OcrResultRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.ocr.ocr_service import OcrService
from app.infrastructure.ocr.label_extraction import extract_label_data
from app.infrastructure.storage.storage_backend import StorageBackend

logger = get_logger()


class ProcessScanOcrUseCase:
    def __init__(
        self,
        scan_repo: ScanRepository,
        ocr_result_repo: OcrResultRepository,
        storage_backend: StorageBackend,
        ocr_service: OcrService,
    ) -> None:
        self.scan_repo = scan_repo
        self.ocr_result_repo = ocr_result_repo
        self.storage_backend = storage_backend
        self.ocr_service = ocr_service

    async def execute(self, scan_id: uuid.UUID, user_id: uuid.UUID) -> OcrProcessResponse:
        scan = await self.scan_repo.get_owned_by_id(scan_id, user_id)
        if scan is None:
            raise NotFoundException("Scan not found", error_code="SCAN_NOT_FOUND")

        existing = await self.ocr_result_repo.get_by_scan_id(scan_id)
        if existing is not None and existing.status == OcrStatus.COMPLETED:
            raise ValidationException("OCR already completed for this scan", error_code="OCR_ALREADY_PROCESSED")

        ocr_row = existing or OcrResult(scan_id=scan_id)
        ocr_row.status = OcrStatus.PROCESSING
        scan.status = ScanStatus.PROCESSING
        scan.processing_stage = ProcessingStage.OCR
        if existing is None:
            self.ocr_result_repo.add(ocr_row)
        await self.scan_repo.flush()
        await self.scan_repo.commit()

        logger.bind(event="OCR_STARTED", scan_id=str(scan_id)).info("OCR started")

        try:
            file_bytes = await self.storage_backend.read(scan.storage_path)
            result = await self.ocr_service.process(file_bytes)
        except Exception as exc:
            ocr_row.status = OcrStatus.FAILED
            ocr_row.error_message = "OCR processing failed"
            scan.status = ScanStatus.FAILED
            scan.retry_count += 1
            await self.scan_repo.commit()
            logger.bind(event="OCR_FAILED", scan_id=str(scan_id), exception_type=type(exc).__name__).error(
                "OCR processing failed"
            )
            raise

        label = extract_label_data(result.text)
        ocr_row.ingredients_text = label.ingredients_text
        # Keep the original OCR and label metadata with its OCR record.  This
        # lets an already-processed scan return the same result on retry
        # without changing scan/upload behaviour or schema.
        ocr_row.bounding_boxes = {
            "raw_text": result.text,
            "product_name": label.product_name,
            "brand": label.brand,
            "category": label.category,
            "nutrition": label.nutrition,
        }
        ocr_row.confidence = result.confidence
        ocr_row.engine = result.engine
        ocr_row.processing_time_ms = result.processing_time_ms
        ocr_row.status = OcrStatus.COMPLETED
        scan.status = ScanStatus.COMPLETED
        scan.processing_stage = ProcessingStage.DONE
        await self.scan_repo.commit()

        logger.bind(
            event="OCR_COMPLETED",
            scan_id=str(scan_id),
            confidence=result.confidence,
            processing_time_ms=result.processing_time_ms,
        ).info("OCR completed")

        return OcrProcessResponse(
            ingredients_text=label.ingredients_text, confidence=result.confidence, engine=result.engine,
            product_name=label.product_name, brand=label.brand, category=label.category, nutrition=label.nutrition,
        )

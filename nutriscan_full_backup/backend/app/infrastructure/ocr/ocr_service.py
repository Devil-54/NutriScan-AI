from __future__ import annotations

import asyncio
import time

from app.core.config import settings
from app.core.exceptions import UnprocessableEntityException
from app.core.logging import get_logger
from app.domain.enums import OcrEngine
from app.infrastructure.ocr.image_preprocessor import preprocess_array
from app.infrastructure.ocr.ocr_engines import BaseOcrEngine, OcrResult

logger = get_logger()


class OcrProcessingResult:
    __slots__ = ("text", "confidence", "engine", "processing_time_ms")

    def __init__(self, text: str, confidence: float, engine: OcrEngine, processing_time_ms: int) -> None:
        self.text = text
        self.confidence = confidence
        self.engine = engine
        self.processing_time_ms = processing_time_ms


class OcrService:
    def __init__(self, primary: BaseOcrEngine, fallback: BaseOcrEngine) -> None:
        self.primary = primary
        self.fallback = fallback

    async def process(self, image_bytes: bytes) -> OcrProcessingResult:
        start = time.perf_counter()

        img, quality = preprocess_array(image_bytes)
        if not quality.is_acceptable:
            raise UnprocessableEntityException(quality.reason or "Image quality too low for OCR", error_code="OCR_LOW_QUALITY_IMAGE")

        result = await self._run_with_timeout(self.primary, img)

        if result is None or result.confidence < settings.OCR_MIN_CONFIDENCE:
            logger.bind(event="OCR_FALLBACK_TRIGGERED").warning(
                f"Primary engine confidence insufficient ({result.confidence if result else 'n/a'}), trying fallback"
            )
            fallback_result = await self._run_with_timeout(self.fallback, img)
            if fallback_result is not None and (result is None or fallback_result.confidence > result.confidence):
                result = fallback_result

        elapsed_ms = int((time.perf_counter() - start) * 1000)

        if result is None:
            raise UnprocessableEntityException("OCR failed on both engines", error_code="OCR_FAILED")

        if not result.text.strip():
            raise UnprocessableEntityException("OCR produced no readable text", error_code="OCR_EMPTY_RESULT")

        return OcrProcessingResult(
            text=result.text, confidence=result.confidence, engine=result.engine, processing_time_ms=elapsed_ms
        )

    async def _run_with_timeout(self, engine: BaseOcrEngine, img) -> OcrResult | None:
        try:
            return await asyncio.wait_for(engine.run(img), timeout=settings.OCR_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.bind(event="OCR_TIMEOUT", engine=engine.engine_name.value).error("OCR engine timed out")
            return None
        except Exception as exc:
            logger.bind(
                event="OCR_ENGINE_ERROR",
                engine=engine.engine_name.value,
                exception_type=type(exc).__name__,
            ).error("OCR engine failed")
            return None

from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image, ImageDraw

from app.core.exceptions import UnprocessableEntityException
from app.domain.enums import OcrEngine
from app.infrastructure.ocr.ocr_engines import BaseOcrEngine, OcrResult
from app.infrastructure.ocr.ocr_service import OcrService

pytestmark = pytest.mark.asyncio


def _sharp_image_bytes(w=800, h=400) -> bytes:
    img = Image.new("RGB", (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    for y in range(20, h - 20, 30):
        draw.line([(20, y), (w - 20, y + 5)], fill=(0, 0, 0), width=4)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class FakeEngine(BaseOcrEngine):
    def __init__(self, engine_name: OcrEngine, text: str, confidence: float, delay: float = 0.0, raise_error: bool = False):
        self.engine_name = engine_name
        self._text = text
        self._confidence = confidence
        self._delay = delay
        self._raise_error = raise_error

    def _run(self, img: np.ndarray) -> OcrResult:
        if self._raise_error:
            raise RuntimeError("engine exploded")
        if self._delay:
            import time

            time.sleep(self._delay)
        return OcrResult(text=self._text, confidence=self._confidence, engine=self.engine_name, boxes=[])


class TestOcrServiceHappyPath:
    async def test_primary_engine_high_confidence_used_directly(self) -> None:
        primary = FakeEngine(OcrEngine.PADDLEOCR, "Sugar, Salt, Water", 95.0)
        fallback = FakeEngine(OcrEngine.PADDLEOCR, "should not be used", 99.0)
        service = OcrService(primary, fallback)

        result = await service.process(_sharp_image_bytes())
        assert result.engine == OcrEngine.PADDLEOCR
        assert result.text == "Sugar, Salt, Water"
        assert result.confidence == 95.0


class TestOcrServiceFallback:
    async def test_low_confidence_triggers_fallback(self) -> None:
        primary = FakeEngine(OcrEngine.PADDLEOCR, "garbled", 30.0)
        fallback = FakeEngine(OcrEngine.PADDLEOCR, "Sugar, Salt", 88.0)
        service = OcrService(primary, fallback)

        result = await service.process(_sharp_image_bytes())
        assert result.engine == OcrEngine.PADDLEOCR
        assert result.confidence == 88.0

    async def test_fallback_not_used_if_worse_than_primary(self) -> None:
        primary = FakeEngine(OcrEngine.PADDLEOCR, "text", 55.0)
        fallback = FakeEngine(OcrEngine.PADDLEOCR, "worse", 40.0)
        service = OcrService(primary, fallback)

        result = await service.process(_sharp_image_bytes())
        assert result.engine == OcrEngine.PADDLEOCR

    async def test_primary_error_falls_back(self) -> None:
        primary = FakeEngine(OcrEngine.PADDLEOCR, "", 0.0, raise_error=True)
        fallback = FakeEngine(OcrEngine.PADDLEOCR, "recovered text", 80.0)
        service = OcrService(primary, fallback)

        result = await service.process(_sharp_image_bytes())
        assert result.engine == OcrEngine.PADDLEOCR
        assert result.text == "recovered text"

    async def test_both_engines_fail_raises(self) -> None:
        primary = FakeEngine(OcrEngine.PADDLEOCR, "", 0.0, raise_error=True)
        fallback = FakeEngine(OcrEngine.PADDLEOCR, "", 0.0, raise_error=True)
        service = OcrService(primary, fallback)

        with pytest.raises(UnprocessableEntityException) as exc_info:
            await service.process(_sharp_image_bytes())
        assert exc_info.value.error_code == "OCR_FAILED"


class TestOcrServiceEdgeCases:
    async def test_empty_text_result_raises(self) -> None:
        primary = FakeEngine(OcrEngine.PADDLEOCR, "   ", 90.0)
        fallback = FakeEngine(OcrEngine.PADDLEOCR, "", 0.0)
        service = OcrService(primary, fallback)

        with pytest.raises(UnprocessableEntityException) as exc_info:
            await service.process(_sharp_image_bytes())
        assert exc_info.value.error_code == "OCR_EMPTY_RESULT"

    async def test_low_quality_image_rejected_before_ocr_runs(self) -> None:
        blurry = Image.new("RGB", (50, 50), color=(255, 255, 255))
        buf = io.BytesIO()
        blurry.save(buf, format="PNG")

        primary = FakeEngine(OcrEngine.PADDLEOCR, "text", 90.0)
        fallback = FakeEngine(OcrEngine.PADDLEOCR, "text", 90.0)
        service = OcrService(primary, fallback)

        with pytest.raises(UnprocessableEntityException) as exc_info:
            await service.process(buf.getvalue())
        assert exc_info.value.error_code == "OCR_LOW_QUALITY_IMAGE"

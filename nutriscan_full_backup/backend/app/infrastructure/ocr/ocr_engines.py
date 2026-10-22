from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from app.core.config import settings
from app.domain.enums import OcrEngine


@dataclass(frozen=True)
class OcrBox:
    text: str
    confidence: float
    points: list[list[float]]


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float
    engine: OcrEngine
    boxes: list[OcrBox]


class BaseOcrEngine(ABC):
    engine_name: OcrEngine

    @abstractmethod
    def _run(self, img: np.ndarray) -> OcrResult: ...

    async def run(self, img: np.ndarray) -> OcrResult:
        return await asyncio.to_thread(self._run, img)


class PaddleOcrEngine(BaseOcrEngine):
    engine_name = OcrEngine.PADDLEOCR

    def __init__(self) -> None:
        os.environ.setdefault("PADDLE_OCR_BASE_DIR", str(Path(settings.OCR_MODEL_DIR).resolve()))
        from paddleocr import PaddleOCR

        self._ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)

    def _run(self, img: np.ndarray) -> OcrResult:
        raw = self._ocr.ocr(img, cls=True)
        boxes: list[OcrBox] = []
        lines: list[str] = []
        confidences: list[float] = []
        for page in raw or []:
            for entry in page or []:
                points, (text, conf) = entry
                if not text:
                    continue
                lines.append(text)
                confidences.append(float(conf) * 100)
                boxes.append(OcrBox(text=text, confidence=float(conf) * 100, points=points))
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        return OcrResult(text="\n".join(lines), confidence=round(avg_conf, 2), engine=self.engine_name, boxes=boxes)


@lru_cache
def get_paddle_engine() -> PaddleOcrEngine:
    return PaddleOcrEngine()

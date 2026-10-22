from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.domain.enums import OcrEngine, OcrStatus


class OcrProcessResponse(BaseModel):
    ingredients_text: str
    confidence: float
    engine: OcrEngine
    product_name: str | None = None
    brand: str | None = None
    category: str | None = None
    nutrition: dict[str, float | None] | None = None


class OcrStatusResponse(BaseModel):
    scan_id: uuid.UUID
    status: OcrStatus
    processing_time_ms: int | None = None


class OcrResultResponse(BaseModel):
    ingredients_text: str
    confidence: float
    engine: OcrEngine
    product_name: str | None = None
    brand: str | None = None
    category: str | None = None
    nutrition: dict[str, float | None] | None = None

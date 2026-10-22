from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import ProcessingStage, ScanStatus


class PersonalizedScanResult(BaseModel):
    """The exact evaluation generated when this scan was completed."""

    status: str
    risk_level: str
    health_score: int
    ingredients: list[str]
    safe_ingredients: list[str]
    unsafe_ingredients: list[str]
    reasons: list[str]
    recommendations: list[str]
    triggered_rules: list[str]
    profile_snapshot: dict | None = None
    nutrition_snapshot: dict | None = None
    alternatives: list[dict] = []
    health_tips: list[str] = []
    nutrition_advice: list[str] = []
    lifestyle_advice: list[str] = []
    ingredient_warnings: list[dict] = []
    confidence_score: int | None = None


class ScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scan_id: uuid.UUID
    original_filename: str
    mime_type: str
    file_size_bytes: int
    width_px: int
    height_px: int
    status: ScanStatus
    processing_stage: ProcessingStage
    retry_count: int
    error_message: str | None
    notes: str | None
    product_name: str | None
    raw_ocr_text: str | None = None
    personalized_result: PersonalizedScanResult | None = None
    created_at: datetime
    updated_at: datetime


class ScanListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scan_id: uuid.UUID
    original_filename: str
    status: ScanStatus
    file_size_bytes: int
    created_at: datetime
    product_name: str | None
    raw_ocr_text: str | None = None
    personalized_result: PersonalizedScanResult | None = None


class ScanHistoryStats(BaseModel):
    """Counts calculated from the authenticated user's persisted scans."""

    total_scans: int
    safe_foods: int
    warnings: int


class ScanStatusRead(BaseModel):
    scan_id: uuid.UUID
    status: ScanStatus
    processing_stage: ProcessingStage
    retry_count: int
    error_message: str | None


class ScanUpdateRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=500)


class ScanUploadResponse(BaseModel):
    scan_id: uuid.UUID
    status: ScanStatus
    original_filename: str
    file_size_bytes: int
    width_px: int
    height_px: int
    checksum_sha256: str

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import OcrEngine, OcrStatus
from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.scan_session import ScanSession


class OcrResult(Base):
    __tablename__ = "ocr_results"

    ocr_result_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scans.scan_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    ingredients_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    engine: Mapped[OcrEngine | None] = mapped_column(Enum(OcrEngine, name="ocr_engine", values_callable=lambda enum: [item.value for item in enum]), nullable=True)
    bounding_boxes: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[OcrStatus] = mapped_column(
        Enum(OcrStatus, name="ocr_status", values_callable=lambda enum: [item.value for item in enum]), nullable=False, default=OcrStatus.PENDING
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    scan: Mapped["ScanSession"] = relationship(back_populates="ocr_result")

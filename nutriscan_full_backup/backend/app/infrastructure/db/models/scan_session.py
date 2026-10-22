from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, SmallInteger, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ProcessingStage, ScanStatus
from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.medical_evaluation import MedicalEvaluation
    from app.infrastructure.db.models.ocr_result import OcrResult
    from app.infrastructure.db.models.user import User


class ScanSession(Base):
    """
    A single food-label scan session: one uploaded image plus its lifecycle
    state. Phase 3B owns everything up through a successful UPLOADED image
    landing in storage. `product_id`, OCR output, and analysis results are
    intentionally NOT modeled here yet - they belong to the OCR/Analysis
    phases and will be added as new nullable columns via a later migration,
    so this table does not need to be redesigned when that phase lands.
    """

    __tablename__ = "scans"

    scan_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

    # ---- File identity ----
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    width_px: Mapped[int] = mapped_column(Integer, nullable=False)
    height_px: Mapped[int] = mapped_column(Integer, nullable=False)

    # ---- Lifecycle ----
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus, name="scan_status", values_callable=lambda enum: [item.value for item in enum]), nullable=False, default=ScanStatus.UPLOADED
    )
    processing_stage: Mapped[ProcessingStage] = mapped_column(
        Enum(ProcessingStage, name="processing_stage", values_callable=lambda enum: [item.value for item in enum]), nullable=False, default=ProcessingStage.NOT_STARTED
    )
    retry_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- User-editable metadata ----
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Captured when the scanner's final personalized evaluation is saved.
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Soft delete / expiration ----
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="scans")
    ocr_result: Mapped["OcrResult | None"] = relationship(
        back_populates="scan", uselist=False, cascade="all, delete-orphan"
    )
    personalized_evaluation: Mapped["MedicalEvaluation | None"] = relationship(
        back_populates="scan", uselist=False
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_terminal(self) -> bool:
        """True once no further state transitions are expected."""
        return self.status in (ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.CANCELLED)

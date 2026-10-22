from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import RiskLevel, VerdictStatus
from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.scan_session import ScanSession
    from app.infrastructure.db.models.user import User


class MedicalEvaluation(Base):
    __tablename__ = "medical_evaluations"

    evaluation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    # Direct medical evaluations may omit a scan. Scanner results always link
    # to their originating scan and are therefore immutable history snapshots.
    scan_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scans.scan_id", ondelete="CASCADE"), unique=True, nullable=True, index=True
    )
    ingredients: Mapped[list] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    status: Mapped[VerdictStatus] = mapped_column(String(20), nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(String(20), nullable=False)
    severity: Mapped[RiskLevel] = mapped_column(String(20), nullable=False)
    health_score: Mapped[int] = mapped_column(Integer, nullable=False)
    reasons: Mapped[list] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    recommendations: Mapped[list] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    safe_ingredients: Mapped[list] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    unsafe_ingredients: Mapped[list] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    triggered_rules: Mapped[list] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    # Point-in-time user data used by the rule engine. This deliberately
    # prevents old reports from changing when a profile is later edited.
    profile_snapshot: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    # Nutrition read from this label at scan time.  Keeping this with the
    # evaluation prevents a later OCR/profile change from rewriting history.
    nutrition_snapshot: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    # ---- Phase 3G: Recommendation Engine (nullable - only set when /recommendation/generate ran) ----
    alternatives: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    health_tips: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    nutrition_advice: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    lifestyle_advice: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    ingredient_warnings: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    confidence_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    user: Mapped["User"] = relationship()
    scan: Mapped["ScanSession | None"] = relationship(back_populates="personalized_evaluation")

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ConditionSeverity
from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.user import User


class MedicalCondition(Base):
    __tablename__ = "medical_conditions"

    condition_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_links: Mapped[list["UserMedicalCondition"]] = relationship(back_populates="condition")


class UserMedicalCondition(Base):
    __tablename__ = "user_medical_conditions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    condition_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("medical_conditions.condition_id", ondelete="CASCADE"), primary_key=True
    )
    severity: Mapped[ConditionSeverity | None] = mapped_column(
        Enum(ConditionSeverity, name="condition_severity", values_callable=lambda enum: [item.value for item in enum]), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped["User"] = relationship(back_populates="medical_conditions")
    condition: Mapped["MedicalCondition"] = relationship(back_populates="user_links")

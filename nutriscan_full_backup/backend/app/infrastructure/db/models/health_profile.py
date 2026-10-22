from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, SmallInteger, Text, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ActivityLevel, DietPreference, FitnessGoal, Gender
from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.user import User


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    age: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name="gender", values_callable=lambda enum: [item.value for item in enum]), nullable=False)
    height_cm: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    bmi: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    activity_level: Mapped[ActivityLevel] = mapped_column(Enum(ActivityLevel, name="activity_level", values_callable=lambda enum: [item.value for item in enum]), nullable=False)
    fitness_goal: Mapped[FitnessGoal] = mapped_column(Enum(FitnessGoal, name="fitness_goal", values_callable=lambda enum: [item.value for item in enum]), nullable=False)
    diet_preference: Mapped[DietPreference] = mapped_column(
        Enum(DietPreference, name="diet_preference", values_callable=lambda enum: [item.value for item in enum]), nullable=False
    )
    pregnancy_status: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    period_status: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    diseases: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="health_profile")

    @staticmethod
    def compute_bmi(height_cm: Decimal, weight_kg: Decimal) -> Decimal:
        """BMI = weight(kg) / height(m)^2. Always server-computed - never accepted from client input."""
        height_m = height_cm / Decimal("100")
        bmi = weight_kg / (height_m * height_m)
        return bmi.quantize(Decimal("0.1"))

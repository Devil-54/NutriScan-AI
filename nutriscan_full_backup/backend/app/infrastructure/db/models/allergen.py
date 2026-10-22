from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import AllergySeverity
from app.infrastructure.db.base import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.user import User


class Allergen(Base):
    """Lookup table: allergens are modeled at the protein/allergen level,
    distinct from `ingredients`, so ingredient-derivative matching can be
    layered on top in a later phase without restructuring this table."""

    __tablename__ = "allergens"

    allergen_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user_links: Mapped[list["UserAllergy"]] = relationship(back_populates="allergen")


class UserAllergy(Base):
    __tablename__ = "user_allergies"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    allergen_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("allergens.allergen_id", ondelete="CASCADE"), primary_key=True
    )
    severity: Mapped[AllergySeverity] = mapped_column(Enum(AllergySeverity, name="allergy_severity", values_callable=lambda enum: [item.value for item in enum]), nullable=False)

    user: Mapped["User"] = relationship(back_populates="allergies")
    allergen: Mapped["Allergen"] = relationship(back_populates="user_links")

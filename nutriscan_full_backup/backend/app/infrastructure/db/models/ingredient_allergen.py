from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class IngredientAllergen(Base):
    __tablename__ = "kg_ingredient_allergens"

    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("kg_ingredients.ingredient_id", ondelete="CASCADE"), primary_key=True
    )
    allergen_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("allergens.allergen_id", ondelete="CASCADE"), primary_key=True
    )
    relationship_type: Mapped[str] = mapped_column(String(20), nullable=False, default="contains")

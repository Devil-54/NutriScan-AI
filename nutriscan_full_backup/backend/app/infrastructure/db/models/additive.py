from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class Additive(Base):
    __tablename__ = "kg_additives"

    additive_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ins_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    common_name: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_category: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ingredient_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("kg_ingredients.ingredient_id", ondelete="SET NULL"), nullable=True
    )

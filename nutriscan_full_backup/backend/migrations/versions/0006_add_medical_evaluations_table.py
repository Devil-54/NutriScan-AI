"""add medical_evaluations table - medical rule engine (phase 3f)

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "medical_evaluations",
        sa.Column("evaluation_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("ingredients", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("health_score", sa.Integer(), nullable=False),
        sa.Column("reasons", postgresql.JSONB(), nullable=False),
        sa.Column("recommendations", postgresql.JSONB(), nullable=False),
        sa.Column("safe_ingredients", postgresql.JSONB(), nullable=False),
        sa.Column("unsafe_ingredients", postgresql.JSONB(), nullable=False),
        sa.Column("triggered_rules", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_medical_evaluations_user_id", "medical_evaluations", ["user_id"])
    op.create_index("ix_medical_evaluations_created_at", "medical_evaluations", ["created_at"])
    op.create_index("ix_medical_evaluations_user_created", "medical_evaluations", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_table("medical_evaluations")

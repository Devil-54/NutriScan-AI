"""extend medical_evaluations with recommendation engine columns (phase 3g)

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("medical_evaluations", sa.Column("alternatives", postgresql.JSONB(), nullable=True))
    op.add_column("medical_evaluations", sa.Column("health_tips", postgresql.JSONB(), nullable=True))
    op.add_column("medical_evaluations", sa.Column("nutrition_advice", postgresql.JSONB(), nullable=True))
    op.add_column("medical_evaluations", sa.Column("lifestyle_advice", postgresql.JSONB(), nullable=True))
    op.add_column("medical_evaluations", sa.Column("ingredient_warnings", postgresql.JSONB(), nullable=True))
    op.add_column("medical_evaluations", sa.Column("confidence_score", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("medical_evaluations", "confidence_score")
    op.drop_column("medical_evaluations", "ingredient_warnings")
    op.drop_column("medical_evaluations", "lifestyle_advice")
    op.drop_column("medical_evaluations", "nutrition_advice")
    op.drop_column("medical_evaluations", "health_tips")
    op.drop_column("medical_evaluations", "alternatives")

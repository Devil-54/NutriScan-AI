"""store label nutrition with personalized scan evaluations

Revision ID: 0012
Revises: 0011
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("medical_evaluations", sa.Column("nutrition_snapshot", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("medical_evaluations", "nutrition_snapshot")

"""store the profile snapshot used for a personalized evaluation

Revision ID: 0011
Revises: 0010
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("medical_evaluations", sa.Column("profile_snapshot", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("medical_evaluations", "profile_snapshot")

"""add free-text allergies and diseases to health profiles

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("health_profiles", sa.Column("allergies", sa.Text(), nullable=True))
    op.add_column("health_profiles", sa.Column("diseases", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("health_profiles", "diseases")
    op.drop_column("health_profiles", "allergies")

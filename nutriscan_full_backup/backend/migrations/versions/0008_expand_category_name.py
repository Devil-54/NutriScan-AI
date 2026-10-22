"""allow full dataset category values

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-01
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("categories", "name", existing_type=sa.String(150), type_=sa.Text())


def downgrade() -> None:
    op.alter_column("categories", "name", existing_type=sa.Text(), type_=sa.String(150))

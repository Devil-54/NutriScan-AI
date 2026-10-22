"""link immutable personalized evaluations to their scan sessions

Revision ID: 0010
Revises: 0009
Create Date: 2026-09-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("scans", sa.Column("product_name", sa.String(length=255), nullable=True))
    op.add_column("medical_evaluations", sa.Column("scan_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_medical_evaluations_scan_id_scans",
        "medical_evaluations",
        "scans",
        ["scan_id"],
        ["scan_id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint("uq_medical_evaluations_scan_id", "medical_evaluations", ["scan_id"])
    op.create_index("ix_medical_evaluations_scan_id", "medical_evaluations", ["scan_id"])


def downgrade() -> None:
    op.drop_index("ix_medical_evaluations_scan_id", table_name="medical_evaluations")
    op.drop_constraint("uq_medical_evaluations_scan_id", "medical_evaluations", type_="unique")
    op.drop_constraint("fk_medical_evaluations_scan_id_scans", "medical_evaluations", type_="foreignkey")
    op.drop_column("medical_evaluations", "scan_id")
    op.drop_column("scans", "product_name")

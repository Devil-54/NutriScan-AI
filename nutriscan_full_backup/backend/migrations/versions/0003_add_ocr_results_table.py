"""add ocr_results table - ocr pipeline (phase 4)

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-18

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ocr_results",
        sa.Column("ocr_result_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "scan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scans.scan_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM("pending", "processing", "completed", "failed", name="ocr_status", create_type=True),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("ingredients_text", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "engine",
            postgresql.ENUM("PaddleOCR", name="ocr_engine", create_type=True),
            nullable=True,
        ),
        sa.Column("bounding_boxes", postgresql.JSONB(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_ocr_results_scan_id", "ocr_results", ["scan_id"])
    op.create_index("ix_ocr_results_status", "ocr_results", ["status"])


def downgrade() -> None:
    op.drop_table("ocr_results")
    for enum_name in ("ocr_status", "ocr_engine"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

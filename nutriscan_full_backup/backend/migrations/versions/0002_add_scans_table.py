"""add scans table - food scan infrastructure (phase 3b)

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("thumbnail_path", sa.String(500), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("width_px", sa.Integer(), nullable=False),
        sa.Column("height_px", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "uploaded", "queued", "processing", "completed", "failed", "cancelled",
                name="scan_status", create_type=True,
            ),
            nullable=False,
            server_default="uploaded",
        ),
        sa.Column(
            "processing_stage",
            postgresql.ENUM(
                "not_started", "ocr", "ingredient_resolution", "risk_analysis", "explanation", "done",
                name="processing_stage", create_type=True,
            ),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("retry_count", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_scans_user_id", "scans", ["user_id"])
    op.create_index("ix_scans_checksum_sha256", "scans", ["checksum_sha256"])
    op.create_index("ix_scans_created_at", "scans", ["created_at"])
    op.create_index("ix_scans_status", "scans", ["status"])
    op.create_index("ix_scans_deleted_at", "scans", ["deleted_at"])
    op.create_index("ix_scans_expires_at", "scans", ["expires_at"])
    # Composite index for the dominant query pattern: a user's active (non-deleted) history, newest first.
    op.create_index(
        "ix_scans_user_active_created",
        "scans",
        ["user_id", "deleted_at", "created_at"],
    )


def downgrade() -> None:
    op.drop_table("scans")
    for enum_name in ("scan_status", "processing_stage"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

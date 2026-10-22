"""initial schema - users, auth, health profile, allergies, conditions, settings, audit

Revision ID: 0001
Revises:
Create Date: 2026-07-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- users ----
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM("user", "admin", name="user_role", create_type=True),
            nullable=False,
            server_default="user",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role", "users", ["role"])

    # ---- refresh_tokens ----
    op.create_table(
        "refresh_tokens",
        sa.Column("token_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("device_info", sa.String(255), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])

    # ---- health_profiles ----
    op.create_table(
        "health_profiles",
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("age", sa.SmallInteger(), nullable=False),
        sa.Column(
            "gender",
            postgresql.ENUM("male", "female", "other", "prefer_not_to_say", name="gender", create_type=True),
            nullable=False,
        ),
        sa.Column("height_cm", sa.Numeric(5, 2), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=False),
        sa.Column("bmi", sa.Numeric(4, 1), nullable=False),
        sa.Column(
            "activity_level",
            postgresql.ENUM(
                "sedentary", "light", "moderate", "active", "very_active", name="activity_level", create_type=True
            ),
            nullable=False,
        ),
        sa.Column(
            "fitness_goal",
            postgresql.ENUM(
                "weight_loss", "muscle_gain", "maintenance", "general_health", name="fitness_goal", create_type=True
            ),
            nullable=False,
        ),
        sa.Column(
            "diet_preference",
            postgresql.ENUM(
                "vegetarian",
                "vegan",
                "non_vegetarian",
                "eggetarian",
                "jain",
                "other",
                name="diet_preference",
                create_type=True,
            ),
            nullable=False,
        ),
        sa.Column("pregnancy_status", sa.Boolean(), nullable=True),
        sa.Column("period_status", sa.Boolean(), nullable=True),
        sa.Column("emergency_notes", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("age BETWEEN 1 AND 120", name="ck_health_profiles_age_range"),
        sa.CheckConstraint("height_cm > 0", name="ck_health_profiles_height_positive"),
        sa.CheckConstraint("weight_kg > 0", name="ck_health_profiles_weight_positive"),
    )
    op.create_unique_constraint("uq_health_profiles_user_id", "health_profiles", ["user_id"])

    # ---- allergens ----
    op.create_table(
        "allergens",
        sa.Column("allergen_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
    )
    op.create_unique_constraint("uq_allergens_name", "allergens", ["name"])

    # ---- user_allergies ----
    op.create_table(
        "user_allergies",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "allergen_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("allergens.allergen_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "severity",
            postgresql.ENUM(
                "mild", "moderate", "severe", "anaphylactic", name="allergy_severity", create_type=True
            ),
            nullable=False,
        ),
    )
    op.create_index("ix_user_allergies_allergen_id", "user_allergies", ["allergen_id"])

    # ---- medical_conditions ----
    op.create_table(
        "medical_conditions",
        sa.Column("condition_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_unique_constraint("uq_medical_conditions_name", "medical_conditions", ["name"])

    # ---- user_medical_conditions ----
    op.create_table(
        "user_medical_conditions",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "condition_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("medical_conditions.condition_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "severity",
            postgresql.ENUM("mild", "moderate", "severe", name="condition_severity", create_type=True),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("diagnosed_at", sa.Date(), nullable=True),
    )
    op.create_index("ix_user_medical_conditions_condition_id", "user_medical_conditions", ["condition_id"])

    # ---- user_settings ----
    op.create_table(
        "user_settings",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("notification_preferences", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("language_preference", sa.String(10), nullable=False, server_default="en"),
        sa.Column(
            "unit_system",
            postgresql.ENUM("metric", "imperial", name="unit_system", create_type=True),
            nullable=False,
            server_default="metric",
        ),
        sa.Column("data_sharing_consent", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ---- audit_logs ----
    op.create_table(
        "audit_logs",
        sa.Column("log_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(150), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("log_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("user_settings")
    op.drop_table("user_medical_conditions")
    op.drop_table("medical_conditions")
    op.drop_table("user_allergies")
    op.drop_table("allergens")
    op.drop_table("health_profiles")
    op.drop_table("refresh_tokens")
    op.drop_table("users")

    # Drop enum types explicitly - Postgres does not cascade-drop these with drop_table.
    for enum_name in (
        "user_role",
        "gender",
        "activity_level",
        "fitness_goal",
        "diet_preference",
        "allergy_severity",
        "condition_severity",
        "unit_system",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

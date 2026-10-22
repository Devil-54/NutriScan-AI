"""add knowledge graph tables - ingredients, nutrition, additives, products (phase 3e)

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("category_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
    )
    op.create_unique_constraint("uq_categories_name", "categories", ["name"])

    op.create_table(
        "kg_ingredients",
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("canonical_name", sa.String(255), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_kg_ingredients_canonical_name", "kg_ingredients", ["canonical_name"])
    op.create_index("ix_kg_ingredients_canonical_name", "kg_ingredients", ["canonical_name"])
    op.create_index("ix_kg_ingredients_external_id", "kg_ingredients", ["external_id"])

    op.create_table(
        "kg_ingredient_aliases",
        sa.Column("alias_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("kg_ingredients.ingredient_id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias_text", sa.String(255), nullable=False),
        sa.Column("alias_type", sa.String(30), nullable=False, server_default="common_name"),
    )
    op.create_index("ix_kg_ingredient_aliases_alias_text", "kg_ingredient_aliases", ["alias_text"])

    op.create_table(
        "kg_ingredient_nutrition",
        sa.Column("nutrition_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("kg_ingredients.ingredient_id", ondelete="CASCADE"), nullable=False),
        sa.Column("calories", sa.Numeric(8, 2), nullable=True),
        sa.Column("protein_g", sa.Numeric(8, 2), nullable=True),
        sa.Column("fat_g", sa.Numeric(8, 2), nullable=True),
        sa.Column("carbohydrates_g", sa.Numeric(8, 2), nullable=True),
        sa.Column("sugar_g", sa.Numeric(8, 2), nullable=True),
        sa.Column("sodium_mg", sa.Numeric(8, 2), nullable=True),
        sa.Column("fiber_g", sa.Numeric(8, 2), nullable=True),
        sa.Column("vitamins", postgresql.JSONB(), nullable=True),
        sa.Column("minerals", postgresql.JSONB(), nullable=True),
    )
    op.create_unique_constraint("uq_kg_ingredient_nutrition_ingredient_id", "kg_ingredient_nutrition", ["ingredient_id"])

    op.create_table(
        "kg_ingredient_allergens",
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("kg_ingredients.ingredient_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("allergen_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("allergens.allergen_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("relationship_type", sa.String(20), nullable=False, server_default="contains"),
    )

    op.create_table(
        "kg_additives",
        sa.Column("additive_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ins_code", sa.String(20), nullable=False),
        sa.Column("common_name", sa.String(255), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("risk_category", sa.String(30), nullable=True),
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("kg_ingredients.ingredient_id", ondelete="SET NULL"), nullable=True),
    )
    op.create_unique_constraint("uq_kg_additives_ins_code", "kg_additives", ["ins_code"])
    op.create_index("ix_kg_additives_ins_code", "kg_additives", ["ins_code"])

    op.create_table(
        "kg_food_products",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(150), nullable=True),
        sa.Column("barcode", sa.String(50), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_kg_food_products_barcode", "kg_food_products", ["barcode"])
    op.create_index("ix_kg_food_products_external_id", "kg_food_products", ["external_id"])

    op.create_table(
        "kg_product_ingredients",
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("kg_food_products.product_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("kg_ingredients.ingredient_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("raw_text", sa.String(255), nullable=True),
    )

    op.create_table(
        "kg_import_jobs",
        sa.Column("job_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("total_rows", sa.Integer(), nullable=True),
        sa.Column("processed_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_duplicate_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("kg_import_jobs")
    op.drop_table("kg_product_ingredients")
    op.drop_table("kg_food_products")
    op.drop_table("kg_additives")
    op.drop_table("kg_ingredient_allergens")
    op.drop_table("kg_ingredient_nutrition")
    op.drop_table("kg_ingredient_aliases")
    op.drop_table("kg_ingredients")
    op.drop_table("categories")

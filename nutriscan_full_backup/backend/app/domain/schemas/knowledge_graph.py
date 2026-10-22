from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class IngredientSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ingredient_id: uuid.UUID
    canonical_name: str
    source: str | None = None


class ProductSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    name: str
    brand: str | None = None
    barcode: str | None = None


class AllergenSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    allergen_id: uuid.UUID
    name: str
    category: str | None = None


class AdditiveSearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    additive_id: uuid.UUID
    ins_code: str
    common_name: str
    purpose: str | None = None
    risk_category: str | None = None


class NutritionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    calories: Decimal | None = None
    protein_g: Decimal | None = None
    fat_g: Decimal | None = None
    carbohydrates_g: Decimal | None = None
    sugar_g: Decimal | None = None
    sodium_mg: Decimal | None = None
    fiber_g: Decimal | None = None
    vitamins: dict | None = None
    minerals: dict | None = None


class ImportDatasetRequest(BaseModel):
    source: str = Field(pattern="^(open_food_facts|usda)$")
    file_path: str = Field(min_length=1, max_length=500)
    batch_size: int = Field(default=500, ge=1, le=5000)


class ImportJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: uuid.UUID
    source: str
    status: str
    total_rows: int | None
    processed_rows: int
    inserted_count: int
    skipped_duplicate_count: int
    error_count: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import RiskLevel, VerdictStatus


class MedicalProfileSummary(BaseModel):
    conditions: list[str]
    allergies: list[str]
    age: int | None
    is_pregnant: bool


class NutritionInput(BaseModel):
    calories: float | None = None
    sugar_g: float | None = None
    sodium_mg: float | None = None
    fat_g: float | None = None
    saturated_fat_g: float | None = None
    protein_g: float | None = None
    fiber_g: float | None = None
    carbohydrates_g: float | None = None
    trans_fat_g: float | None = None
    cholesterol_mg: float | None = None
    potassium_mg: float | None = None
    calcium_mg: float | None = None
    iron_mg: float | None = None


class EvaluateRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1)
    nutrition: NutritionInput | None = None
    allergen_names: list[str] = Field(default_factory=list)


class EvaluateResponse(BaseModel):
    status: VerdictStatus
    risk_level: RiskLevel
    severity: RiskLevel
    health_score: int
    reasons: list[str]
    recommendations: list[str]
    safe_ingredients: list[str]
    unsafe_ingredients: list[str]
    triggered_rules: list[str]


class EvaluationHistoryItem(BaseModel):
    evaluation_id: uuid.UUID
    status: VerdictStatus
    risk_level: RiskLevel
    health_score: int
    unsafe_ingredients: list[str]
    created_at: datetime

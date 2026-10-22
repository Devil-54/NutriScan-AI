from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import RiskLevel, VerdictStatus
from app.domain.schemas.medical import NutritionInput


class RecommendationRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1)
    scan_id: uuid.UUID | None = None
    product_name: str | None = Field(default=None, max_length=255)
    nutrition: NutritionInput | None = None
    allergen_names: list[str] = Field(default_factory=list)


class AlternativeItem(BaseModel):
    suggestion: str
    reason: str


class IngredientWarningItem(BaseModel):
    ingredient: str
    reason: str


class RecommendationResponse(BaseModel):
    status: VerdictStatus
    risk_level: RiskLevel
    safe_foods: list[str]
    unsafe_foods: list[str]
    alternatives: list[AlternativeItem]
    health_tips: list[str]
    nutrition_advice: list[str]
    lifestyle_advice: list[str]
    ingredient_warnings: list[IngredientWarningItem]
    recommendation_score: int
    confidence_score: int
    reasons: list[str]


class RecommendationHistoryItem(BaseModel):
    evaluation_id: uuid.UUID
    status: VerdictStatus
    recommendation_score: int
    confidence_score: int | None
    unsafe_foods: list[str]
    created_at: datetime

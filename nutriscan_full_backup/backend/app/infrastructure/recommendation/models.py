from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IngredientWarning:
    ingredient: str
    reason: str


@dataclass
class Alternative:
    suggestion: str
    reason: str


@dataclass
class RecommendationResult:
    safe_foods: list[str] = field(default_factory=list)
    unsafe_foods: list[str] = field(default_factory=list)
    alternatives: list[Alternative] = field(default_factory=list)
    health_tips: list[str] = field(default_factory=list)
    nutrition_advice: list[str] = field(default_factory=list)
    lifestyle_advice: list[str] = field(default_factory=list)
    ingredient_warnings: list[IngredientWarning] = field(default_factory=list)
    recommendation_score: int = 100
    confidence_score: int = 50
    reasons: list[str] = field(default_factory=list)

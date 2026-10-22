from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import RuleConditionKey, VerdictStatus
from app.infrastructure.db.models.health_profile import HealthProfile
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.medical_rules.engine import EngineVerdict
from app.infrastructure.medical_rules.rule_context import RuleContext
from app.infrastructure.recommendation.content import (
    ALTERNATIVE_TEMPLATES,
    GENERIC_HEALTH_TIP,
    GENERIC_LIFESTYLE_TIP,
    HEALTH_TIPS,
    LIFESTYLE_ADVICE,
    NUTRITION_ADVICE,
    detect_trigger_categories,
)
from app.infrastructure.recommendation.explainer import RecommendationExplainer, RuleBasedExplainer
from app.infrastructure.recommendation.models import Alternative, IngredientWarning, RecommendationResult

_CONFIDENCE_FLOOR = 40
_CONFIDENCE_CEILING = 95


@dataclass
class PersonalizationProfile:
    """Fields Phase 3F's RuleContext doesn't carry but recommendations should
    consider - fetched directly from the existing HealthProfile, not
    duplicated as new input."""

    age: int | None = None
    gender: str | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    bmi: float | None = None
    diet_preference: str | None = None
    fitness_goal: str | None = None
    is_pregnant: bool = False

    @property
    def displayed_fitness_goal(self) -> str | None:
        """Pregnancy always takes precedence over a stale weight-loss setting."""
        return "healthy_pregnancy_weight_gain" if self.is_pregnant else self.fitness_goal

    @classmethod
    def from_health_profile(cls, profile: HealthProfile | None) -> "PersonalizationProfile":
        if profile is None:
            return cls()
        return cls(
            age=profile.age,
            gender=profile.gender.value if profile.gender else None,
            weight_kg=float(profile.weight_kg) if profile.weight_kg is not None else None,
            height_cm=float(profile.height_cm) if profile.height_cm is not None else None,
            bmi=float(profile.bmi) if profile.bmi is not None else None,
            diet_preference=profile.diet_preference.value if profile.diet_preference else None,
            fitness_goal=profile.fitness_goal.value if profile.fitness_goal else None,
            is_pregnant=bool(profile.pregnancy_status),
        )


class RecommendationEngine:
    """
    Reuses the Medical Rule Engine's verdict directly (no re-evaluation) -
    this engine only layers presentation/personalization on top of an
    already-computed EngineVerdict, per the "avoid duplicate calculations"
    requirement.
    """

    def __init__(
        self,
        explainer: RecommendationExplainer | None = None,
        product_repo: FoodProductRepository | None = None,
    ) -> None:
        self.explainer = explainer or RuleBasedExplainer()
        self.product_repo = product_repo

    async def generate(
        self,
        verdict: EngineVerdict,
        context: RuleContext,
        profile: PersonalizationProfile,
        kg_match_ratio: float = 0.0,
    ) -> RecommendationResult:
        trigger_categories = detect_trigger_categories(verdict.reasons)

        ingredient_warnings = [
            IngredientWarning(
                ingredient=ingredient,
                reason=self.explainer.explain_unsafe_ingredient(ingredient, verdict.reasons),
            )
            for ingredient in verdict.unsafe_ingredients
        ]

        alternatives = await self._build_alternatives(trigger_categories, context)

        health_tips = self._collect_condition_content(HEALTH_TIPS, context.user_conditions) or [GENERIC_HEALTH_TIP]
        nutrition_advice = self._collect_condition_content(NUTRITION_ADVICE, context.user_conditions)
        lifestyle_advice = self._collect_condition_content(LIFESTYLE_ADVICE, context.user_conditions) or [
            GENERIC_LIFESTYLE_TIP
        ]

        nutrition_advice = self._personalize_nutrition_advice(nutrition_advice, profile)

        confidence_score = self._compute_confidence(kg_match_ratio, verdict)

        return RecommendationResult(
            safe_foods=verdict.safe_ingredients,
            unsafe_foods=verdict.unsafe_ingredients,
            alternatives=alternatives,
            health_tips=health_tips,
            nutrition_advice=nutrition_advice,
            lifestyle_advice=lifestyle_advice,
            ingredient_warnings=ingredient_warnings,
            recommendation_score=verdict.health_score,
            confidence_score=confidence_score,
            reasons=verdict.reasons,
        )

    async def _build_alternatives(self, trigger_categories: list[str], context: RuleContext) -> list[Alternative]:
        if not trigger_categories:
            return []

        alternatives: list[Alternative] = []
        for category in trigger_categories:
            for suggestion in ALTERNATIVE_TEMPLATES.get(category, [])[:2]:
                alternatives.append(
                    Alternative(suggestion=suggestion, reason=self.explainer.explain_alternative(suggestion, category))
                )

        # If the Knowledge Graph has real product data, prefer concrete product names
        # over generic templates for the first category (richer once datasets are imported).
        if self.product_repo and trigger_categories:
            try:
                kg_products = await self.product_repo.search(trigger_categories[0], limit=3)
            except Exception:  # noqa: BLE001 - KG lookup is best-effort, never blocks recommendations
                kg_products = []
            for product in kg_products:
                alternatives.append(
                    Alternative(
                        suggestion=product.name,
                        reason=self.explainer.explain_alternative(product.name, trigger_categories[0]),
                    )
                )

        return alternatives

    @staticmethod
    def _collect_condition_content(source: dict[RuleConditionKey, list[str]], conditions: set[RuleConditionKey]) -> list[str]:
        items: list[str] = []
        for condition in conditions:
            items.extend(source.get(condition, []))
        return list(dict.fromkeys(items))

    @staticmethod
    def _personalize_nutrition_advice(advice: list[str], profile: PersonalizationProfile) -> list[str]:
        personalized = list(advice)
        if profile.is_pregnant and "pregnan" not in " ".join(advice).lower():
            personalized.append("As you are pregnant, prioritize folate, iron, and calcium-rich foods.")
            personalized.append(
                "Aim for healthy pregnancy weight gain rather than weight loss; discuss an individualized goal with your healthcare professional."
            )
        if profile.bmi is not None and profile.bmi >= 30:
            personalized.append("Your recorded BMI suggests extra care with portion sizes and calorie-dense foods.")
        if profile.diet_preference in ("vegetarian", "vegan"):
            personalized.append("Ensure adequate plant-based protein and B12 intake for your diet preference.")
        return personalized

    @staticmethod
    def _compute_confidence(kg_match_ratio: float, verdict: EngineVerdict) -> int:
        """Higher when more ingredients resolved against real Knowledge Graph
        data; lower (but never near-zero) when relying on keyword fallbacks
        only - this is what makes confidence 'automatically improve' once
        datasets are imported, with no code change required here."""
        base = _CONFIDENCE_FLOOR + int(kg_match_ratio * (_CONFIDENCE_CEILING - _CONFIDENCE_FLOOR))
        if verdict.status == VerdictStatus.SAFE and not verdict.triggered_rules:
            base = max(base, 60)  # a clean "safe, nothing triggered" verdict is inherently more certain
        return max(0, min(100, base))

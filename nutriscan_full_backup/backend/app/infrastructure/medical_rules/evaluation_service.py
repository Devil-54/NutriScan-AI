from __future__ import annotations

import uuid

from app.core.logging import get_logger

from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.db.repositories.nutrition_repository import NutritionRepository
from app.infrastructure.medical_rules.context_builder import MedicalContextBuilder
from app.infrastructure.medical_rules.engine import EngineVerdict, RuleEngine
from app.infrastructure.medical_rules.rule_context import NutritionSnapshot, RuleContext

_NUTRITION_FIELDS = ("calories", "sugar_g", "sodium_mg", "fat_g", "protein_g", "fiber_g", "carbohydrates_g")
logger = get_logger()


class ProductEvaluationService:
    """
    Shared "resolve ingredients against the Knowledge Graph, build a
    RuleContext, run the Medical Rule Engine" pipeline. Extracted so
    EvaluateProductUseCase (Phase 3F) and GenerateRecommendationUseCase
    (Phase 3G) call the exact same resolution/evaluation path instead of
    each re-implementing it - avoids duplicate KG lookups and keeps the two
    features from drifting apart.
    """

    def __init__(
        self,
        context_builder: MedicalContextBuilder,
        engine: RuleEngine,
        ingredient_repo: IngredientRepository | None = None,
        nutrition_repo: NutritionRepository | None = None,
        allergen_repo: AllergenRepository | None = None,
    ) -> None:
        self.context_builder = context_builder
        self.engine = engine
        self.ingredient_repo = ingredient_repo
        self.nutrition_repo = nutrition_repo
        self.allergen_repo = allergen_repo

    async def resolve_from_kg(self, ingredients: list[str]) -> tuple[NutritionSnapshot, list[str], float]:
        """Returns (aggregated nutrition, allergen names, kg_match_ratio).
        kg_match_ratio (0-1) is how many of the given ingredients resolved
        to a Knowledge Graph entry - used as a confidence signal by the
        recommendation engine (more real data = more confident advice)."""
        totals: dict[str, float] = {f: 0.0 for f in _NUTRITION_FIELDS}
        found_any = {f: False for f in _NUTRITION_FIELDS}
        allergen_names: set[str] = set()
        matched_count = 0

        if not (self.ingredient_repo and self.nutrition_repo and self.allergen_repo) or not ingredients:
            return NutritionSnapshot(), [], 0.0

        for raw_name in ingredients:
            try:
                matches = await self.ingredient_repo.search_by_alias(raw_name, limit=1)
                if not matches:
                    matches = await self.ingredient_repo.search(raw_name, limit=1)
                if not matches:
                    logger.bind(event="KG_INGREDIENT_UNRESOLVED").info("Ingredient was not found in KG")
                    continue
                matched_count += 1
                ingredient = matches[0]

                nutrition = await self.nutrition_repo.get_by_ingredient_id(ingredient.ingredient_id)
                if nutrition:
                    for field in _NUTRITION_FIELDS:
                        value = getattr(nutrition, field, None)
                        if value is not None:
                            totals[field] += float(value)
                            found_any[field] = True

                allergens = await self.allergen_repo.get_allergens_for_ingredient(ingredient.ingredient_id)
                allergen_names.update(a.name for a in allergens)
            except Exception:
                logger.bind(event="KG_INGREDIENT_FAILED").error("KG lookup failed for one ingredient; continuing")

        snapshot = NutritionSnapshot(**{f: (totals[f] if found_any[f] else None) for f in _NUTRITION_FIELDS})
        match_ratio = matched_count / len(ingredients) if ingredients else 0.0
        return snapshot, sorted(allergen_names), match_ratio

    @staticmethod
    def merge_nutrition(caller: NutritionSnapshot | None, kg: NutritionSnapshot) -> NutritionSnapshot:
        base = caller or NutritionSnapshot()
        merged = {}
        for field in _NUTRITION_FIELDS + ("saturated_fat_g", "trans_fat_g", "cholesterol_mg", "potassium_mg", "calcium_mg", "iron_mg"):
            caller_value = getattr(base, field, None)
            merged[field] = caller_value if caller_value is not None else getattr(kg, field, None)
        return NutritionSnapshot(**merged)

    async def evaluate(
        self,
        user_id: uuid.UUID,
        ingredients: list[str],
        nutrition: NutritionSnapshot | None = None,
        allergen_names: list[str] | None = None,
    ) -> tuple[EngineVerdict, RuleContext, float]:
        logger.bind(event="KG_LOOKUP_START", ingredient_count=len(ingredients)).info("KG lookup started")
        kg_nutrition, kg_allergen_names, kg_match_ratio = await self.resolve_from_kg(ingredients)
        logger.bind(event="KG_LOOKUP_COMPLETE", match_ratio=kg_match_ratio).info("KG lookup completed")
        merged_nutrition = self.merge_nutrition(nutrition, kg_nutrition)
        merged_allergens = sorted(set(allergen_names or []) | set(kg_allergen_names))

        context = await self.context_builder.build_context(
            user_id=user_id, ingredients=ingredients, nutrition=merged_nutrition, allergen_names=merged_allergens
        )
        logger.bind(event="PROFILE_LOADED", user_id=str(user_id)).info("Latest user profile loaded")
        logger.bind(event="MEDICAL_RULE_EVALUATION_START", user_id=str(user_id)).info("Medical rule evaluation started")
        verdict = self.engine.evaluate(context)
        logger.bind(event="MEDICAL_RULE_EVALUATION_COMPLETE", triggered_rules=verdict.triggered_rules).info(
            "Medical rule evaluation completed"
        )
        return verdict, context, kg_match_ratio

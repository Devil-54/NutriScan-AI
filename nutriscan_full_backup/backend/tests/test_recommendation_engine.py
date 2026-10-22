from __future__ import annotations

import pytest

from app.domain.enums import RuleConditionKey, VerdictStatus
from app.infrastructure.medical_rules.engine import RuleEngine
from app.infrastructure.medical_rules.rule_context import NutritionSnapshot, RuleContext
from app.infrastructure.recommendation.engine import PersonalizationProfile, RecommendationEngine

pytestmark = pytest.mark.asyncio

rule_engine = RuleEngine()
rec_engine = RecommendationEngine()


def _ctx(**kwargs) -> RuleContext:
    defaults = dict(
        ingredients=[], allergen_names=[], nutrition=NutritionSnapshot(), user_conditions=set(), user_allergy_names=set()
    )
    defaults.update(kwargs)
    return RuleContext(**defaults)


async def _generate(context: RuleContext, profile: PersonalizationProfile | None = None):
    verdict = rule_engine.evaluate(context)
    result = await rec_engine.generate(verdict, context, profile or PersonalizationProfile(), kg_match_ratio=0.0)
    return verdict, result


class TestDiabetesRecommendation:
    async def test_high_sugar_generates_sugar_alternatives(self) -> None:
        ctx = _ctx(user_conditions={RuleConditionKey.DIABETES}, nutrition=NutritionSnapshot(sugar_g=25), ingredients=["Sugar"])
        verdict, result = await _generate(ctx)
        assert any("sugar" in a.suggestion.lower() for a in result.alternatives)
        assert any("diabetes" in tip.lower() or "carbohydrate" in tip.lower() for tip in result.health_tips)
        assert result.recommendation_score < 100

    async def test_ingredient_warning_has_reason(self) -> None:
        ctx = _ctx(user_conditions={RuleConditionKey.DIABETES}, nutrition=NutritionSnapshot(sugar_g=25), ingredients=["Sugar"])
        verdict, result = await _generate(ctx)
        assert len(result.ingredient_warnings) >= 1
        assert all(w.reason for w in result.ingredient_warnings)


class TestHypertensionRecommendation:
    async def test_high_sodium_generates_low_sodium_alternatives(self) -> None:
        ctx = _ctx(user_conditions={RuleConditionKey.HYPERTENSION}, nutrition=NutritionSnapshot(sodium_mg=900))
        verdict, result = await _generate(ctx)
        assert any("sodium" in a.suggestion.lower() for a in result.alternatives)
        assert verdict.status == VerdictStatus.UNSAFE


class TestPregnancyRecommendation:
    async def test_unsafe_ingredient_flagged_with_reason(self) -> None:
        ctx = _ctx(ingredients=["Alcohol"], is_pregnant=True)
        verdict, result = await _generate(ctx)
        assert verdict.status == VerdictStatus.UNSAFE
        assert len(result.ingredient_warnings) >= 1

    async def test_pregnancy_personalization_adds_nutrition_advice(self) -> None:
        ctx = _ctx(ingredients=["Rice"], is_pregnant=True, user_conditions={RuleConditionKey.PREGNANCY})
        profile = PersonalizationProfile(is_pregnant=True)
        verdict, result = await _generate(ctx, profile)
        assert any("folate" in a.lower() or "iron" in a.lower() or "pregnan" in a.lower() for a in result.nutrition_advice)


class TestFoodAllergyRecommendation:
    async def test_matched_allergen_generates_allergen_free_alternative(self) -> None:
        ctx = _ctx(allergen_names=["Peanut protein"], user_allergy_names={"Peanut protein"})
        verdict, result = await _generate(ctx)
        assert verdict.status == VerdictStatus.UNSAFE
        assert len(result.ingredient_warnings) >= 1
        assert result.confidence_score >= 40


class TestWeightLossRecommendation:
    async def test_high_calorie_flagged(self) -> None:
        ctx = _ctx(user_conditions={RuleConditionKey.WEIGHT_LOSS}, nutrition=NutritionSnapshot(calories=400))
        verdict, result = await _generate(ctx)
        assert verdict.status == VerdictStatus.WARNING
        assert any("weight" in tip.lower() or "portion" in tip.lower() or "satiety" in tip.lower() for tip in result.health_tips)


class TestWeightGainRecommendation:
    async def test_protein_source_is_safe_no_warnings(self) -> None:
        ctx = _ctx(user_conditions={RuleConditionKey.WEIGHT_GAIN}, ingredients=["Whey Protein"])
        verdict, result = await _generate(ctx)
        assert verdict.status == VerdictStatus.SAFE
        assert result.ingredient_warnings == []
        assert "Whey Protein" in result.safe_foods


class TestSportsNutritionRecommendation:
    async def test_protein_ingredient_safe(self) -> None:
        ctx = _ctx(user_conditions={RuleConditionKey.SPORTS_NUTRITION}, ingredients=["Soy Protein"])
        verdict, result = await _generate(ctx)
        assert verdict.status == VerdictStatus.SAFE
        assert result.recommendation_score == 100


class TestMultipleDiseases:
    async def test_combines_tips_from_all_conditions(self) -> None:
        ctx = _ctx(
            ingredients=["Sugar", "Salt"],
            user_conditions={RuleConditionKey.DIABETES, RuleConditionKey.HYPERTENSION},
            nutrition=NutritionSnapshot(sugar_g=25, sodium_mg=900),
        )
        verdict, result = await _generate(ctx)
        tips_text = " ".join(result.health_tips).lower()
        assert "carbohydrate" in tips_text or "fiber" in tips_text
        assert "sodium" in tips_text or "potassium" in tips_text


class TestRecommendationConflicts:
    async def test_conflicting_conditions_do_not_cancel_each_other(self) -> None:
        """Weight-gain rule likes protein (SAFE-positive); diabetes rule flags sugar
        (UNSAFE). Both signals must independently surface, not cancel out."""
        ctx = _ctx(
            ingredients=["Whey Protein", "Sugar"],
            user_conditions={RuleConditionKey.WEIGHT_GAIN, RuleConditionKey.DIABETES},
            nutrition=NutritionSnapshot(sugar_g=25),
        )
        verdict, result = await _generate(ctx)
        assert verdict.status == VerdictStatus.UNSAFE
        assert "Whey Protein" in result.safe_foods
        assert any(w.ingredient.lower() == "sugar" for w in result.ingredient_warnings) or "sugar" in [
            u.lower() for u in result.unsafe_foods
        ]


class TestInvalidInputsAndBounds:
    async def test_empty_context_is_safe(self) -> None:
        ctx = _ctx()
        verdict, result = await _generate(ctx)
        assert verdict.status == VerdictStatus.SAFE
        assert 0 <= result.confidence_score <= 100
        assert 0 <= result.recommendation_score <= 100

    async def test_confidence_score_bounded_with_full_kg_match(self) -> None:
        ctx = _ctx(ingredients=["Sugar"], user_conditions={RuleConditionKey.DIABETES}, nutrition=NutritionSnapshot(sugar_g=25))
        verdict = rule_engine.evaluate(ctx)
        result = await rec_engine.generate(verdict, ctx, PersonalizationProfile(), kg_match_ratio=1.0)
        assert 0 <= result.confidence_score <= 100

    async def test_no_ingredients_no_conditions_returns_empty_lists(self) -> None:
        ctx = _ctx()
        verdict, result = await _generate(ctx)
        assert result.unsafe_foods == []
        assert result.ingredient_warnings == []

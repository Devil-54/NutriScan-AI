from __future__ import annotations

from app.domain.enums import RiskLevel, RuleConditionKey, VerdictStatus
from app.infrastructure.medical_rules.engine import RuleEngine
from app.infrastructure.medical_rules.rule_context import NutritionSnapshot, RuleContext

engine = RuleEngine()


def _ctx(**kwargs) -> RuleContext:
    defaults = dict(ingredients=[], allergen_names=[], nutrition=NutritionSnapshot(), user_conditions=set(), user_allergy_names=set())
    defaults.update(kwargs)
    return RuleContext(**defaults)


class TestDiabetesRule:
    def test_high_sugar_unsafe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.DIABETES}, nutrition=NutritionSnapshot(sugar_g=25)))
        assert v.status == VerdictStatus.UNSAFE
        assert "diabetes" in " ".join(v.reasons).lower() or v.unsafe_ingredients is not None

    def test_moderate_sugar_warning(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.DIABETES}, nutrition=NutritionSnapshot(sugar_g=12)))
        assert v.status == VerdictStatus.WARNING

    def test_no_sugar_safe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.DIABETES}, ingredients=["Water", "Salt"], nutrition=NutritionSnapshot(sugar_g=0)))
        assert v.status == VerdictStatus.SAFE

    def test_ingredient_keyword_without_nutrition_data(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.DIABETES}, ingredients=["Sugar", "Wheat Flour"]))
        assert v.status == VerdictStatus.WARNING


class TestHypertensionRule:
    def test_high_sodium_unsafe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.HYPERTENSION}, nutrition=NutritionSnapshot(sodium_mg=850)))
        assert v.status == VerdictStatus.UNSAFE
        assert v.risk_level == RiskLevel.HIGH

    def test_moderate_sodium_warning(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.HYPERTENSION}, nutrition=NutritionSnapshot(sodium_mg=500)))
        assert v.status == VerdictStatus.WARNING

    def test_boundary_exactly_800_is_unsafe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.HYPERTENSION}, nutrition=NutritionSnapshot(sodium_mg=800)))
        assert v.status == VerdictStatus.UNSAFE

    def test_boundary_just_below_400_is_safe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.HYPERTENSION}, nutrition=NutritionSnapshot(sodium_mg=399)))
        assert v.status == VerdictStatus.SAFE


class TestKidneyDiseaseRule:
    def test_phosphate_additive_unsafe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.KIDNEY_DISEASE}, ingredients=["Sodium Phosphate"]))
        assert v.status == VerdictStatus.UNSAFE

    def test_no_risk_ingredients_safe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.KIDNEY_DISEASE}, ingredients=["Rice", "Water"]))
        assert v.status == VerdictStatus.SAFE


class TestPregnancyRule:
    def test_alcohol_unsafe(self) -> None:
        v = engine.evaluate(_ctx(is_pregnant=True, ingredients=["Alcohol"]))
        assert v.status == VerdictStatus.UNSAFE

    def test_not_pregnant_ignored(self) -> None:
        v = engine.evaluate(_ctx(is_pregnant=False, ingredients=["Alcohol"]))
        assert v.status == VerdictStatus.SAFE

    def test_safe_food_while_pregnant(self) -> None:
        v = engine.evaluate(_ctx(is_pregnant=True, ingredients=["Rice", "Water"]))
        assert v.status == VerdictStatus.SAFE


class TestAllergyRule:
    def test_matched_allergen_critical(self) -> None:
        v = engine.evaluate(_ctx(user_allergy_names={"Peanut protein"}, allergen_names=["Peanut protein"]))
        assert v.status == VerdictStatus.UNSAFE
        assert v.risk_level == RiskLevel.CRITICAL

    def test_ingredient_text_fallback_match(self) -> None:
        v = engine.evaluate(_ctx(user_allergy_names={"Peanut protein"}, ingredients=["Peanut Butter"]))
        assert v.status == VerdictStatus.UNSAFE

    def test_no_allergies_no_trigger(self) -> None:
        v = engine.evaluate(_ctx(user_allergy_names=set(), ingredients=["Peanut Butter"]))
        assert v.status == VerdictStatus.SAFE

    def test_unrelated_allergy_not_triggered(self) -> None:
        v = engine.evaluate(_ctx(user_allergy_names={"Gluten"}, ingredients=["Peanut Butter"]))
        assert v.status == VerdictStatus.SAFE


class TestPcosRule:
    def test_refined_carbs_warning(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.PCOS}, ingredients=["Maida"]))
        assert v.status == VerdictStatus.WARNING


class TestWeightLossRule:
    def test_high_calorie_warning(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.WEIGHT_LOSS}, nutrition=NutritionSnapshot(calories=400)))
        assert v.status == VerdictStatus.WARNING

    def test_low_calorie_safe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.WEIGHT_LOSS}, ingredients=["Cucumber"], nutrition=NutritionSnapshot(calories=50)))
        assert v.status == VerdictStatus.SAFE


class TestWeightGainRule:
    def test_protein_source_safe_with_positive_reason(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.WEIGHT_GAIN}, ingredients=["Whey Protein"]))
        assert v.status == VerdictStatus.SAFE
        assert any("protein" in r.lower() for r in v.reasons)


class TestSportsNutritionRule:
    def test_protein_positive(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.SPORTS_NUTRITION}, ingredients=["Soy Protein"]))
        assert v.status == VerdictStatus.SAFE

    def test_sugar_only_warning(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.SPORTS_NUTRITION}, ingredients=["Sugar"]))
        assert v.status == VerdictStatus.WARNING


class TestHighCholesterolRule:
    def test_trans_fat_unsafe(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.HIGH_CHOLESTEROL}, ingredients=["Partially Hydrogenated Oil"]))
        assert v.status == VerdictStatus.UNSAFE

    def test_moderate_saturated_fat_warning(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.HIGH_CHOLESTEROL}, nutrition=NutritionSnapshot(saturated_fat_g=6)))
        assert v.status == VerdictStatus.WARNING


class TestMultipleConditionsAndConflicts:
    def test_multiple_conditions_worst_status_wins(self) -> None:
        v = engine.evaluate(_ctx(
            user_conditions={RuleConditionKey.DIABETES, RuleConditionKey.HYPERTENSION},
            ingredients=["Sugar", "Salt"],
            nutrition=NutritionSnapshot(sugar_g=25, sodium_mg=900),
        ))
        assert v.status == VerdictStatus.UNSAFE
        assert v.risk_level == RiskLevel.HIGH
        assert len(v.triggered_rules) >= 2

    def test_conflict_weight_gain_safe_vs_diabetes_unsafe(self) -> None:
        """A sugary high-protein product: WeightGainRule says SAFE, DiabetesRule says UNSAFE -
        overall verdict must reflect the unsafe finding, not be diluted by the positive one."""
        v = engine.evaluate(_ctx(
            user_conditions={RuleConditionKey.DIABETES, RuleConditionKey.WEIGHT_GAIN},
            ingredients=["Sugar", "Whey Protein"],
            nutrition=NutritionSnapshot(sugar_g=25),
        ))
        assert v.status == VerdictStatus.UNSAFE
        assert any("protein" in r.lower() for r in v.reasons)  # positive reason still surfaced

    def test_allergy_overrides_other_safe_conditions(self) -> None:
        v = engine.evaluate(_ctx(
            user_conditions={RuleConditionKey.WEIGHT_GAIN},
            user_allergy_names={"Peanut protein"},
            ingredients=["Peanut Butter", "Whey Protein"],
        ))
        assert v.status == VerdictStatus.UNSAFE
        assert v.risk_level == RiskLevel.CRITICAL

    def test_baseline_product_quality_risks_apply_without_profile_conditions(self) -> None:
        v = engine.evaluate(_ctx(ingredients=["Sugar", "Salt", "Hydrogenated Oil"]))
        assert v.status == VerdictStatus.UNSAFE
        assert v.health_score == 75


class TestBoundaryAndInvalidInputs:
    def test_empty_ingredients_list(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.DIABETES}, ingredients=[]))
        assert v.status == VerdictStatus.SAFE

    def test_health_score_never_negative(self) -> None:
        v = engine.evaluate(_ctx(
            user_conditions={RuleConditionKey.DIABETES, RuleConditionKey.HYPERTENSION, RuleConditionKey.KIDNEY_DISEASE, RuleConditionKey.HEART_DISEASE},
            user_allergy_names={"Peanut protein"},
            ingredients=["Sugar", "Salt", "Peanut Butter", "Hydrogenated Oil", "Sodium Phosphate"],
            nutrition=NutritionSnapshot(sugar_g=30, sodium_mg=900),
        ))
        assert v.health_score >= 0

    def test_missing_nutrition_data_does_not_crash(self) -> None:
        v = engine.evaluate(_ctx(user_conditions={RuleConditionKey.DIABETES}, ingredients=["Water"], nutrition=NutritionSnapshot()))
        assert v.status == VerdictStatus.SAFE

    def test_high_label_sugar_is_a_baseline_product_quality_concern(self) -> None:
        v = engine.evaluate(_ctx(ingredients=["Sugar"], nutrition=NutritionSnapshot(sugar_g=30)))
        assert v.status == VerdictStatus.UNSAFE
        assert v.health_score == 75


class TestDemoProductQualityRules:
    def test_maggi_label_retains_its_existing_single_moderate_deduction(self) -> None:
        verdict = engine.evaluate(_ctx(ingredients=[
            "refined wheat flour", "palm oil", "iodized salt", "flavour enhancer INS 621",
        ]))
        assert verdict.health_score == 88
        assert verdict.risk_level == RiskLevel.MODERATE
        assert "palm oil" in verdict.unsafe_ingredients

    def test_lays_label_has_three_moderate_deductions(self) -> None:
        verdict = engine.evaluate(_ctx(
            ingredients=["potatoes", "vegetable oil", "sunflower oil", "corn oil", "canola oil", "salt"],
            nutrition=NutritionSnapshot(fat_g=10, saturated_fat_g=1.5, sodium_mg=170, fiber_g=1, protein_g=2),
        ))
        assert verdict.health_score == 64
        assert verdict.risk_level == RiskLevel.MODERATE
        assert "low dietary fiber" in verdict.unsafe_ingredients

    def test_quaker_label_remains_unchanged(self) -> None:
        verdict = engine.evaluate(_ctx(
            ingredients=["whole grain oats", "calcium carbonate", "salt", "reduced iron"],
            nutrition=NutritionSnapshot(fat_g=2, saturated_fat_g=0.5, sodium_mg=75, fiber_g=3, protein_g=4),
        ))
        assert verdict.health_score == 100
        assert verdict.risk_level == RiskLevel.LOW

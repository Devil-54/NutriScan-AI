from __future__ import annotations

from app.domain.enums import RiskLevel, RuleConditionKey, VerdictStatus
from app.infrastructure.medical_rules.rule_base import BaseRule, any_ingredient_matches
from app.infrastructure.medical_rules.rule_context import RuleContext, RuleResult

_SUGAR_KEYWORDS = ["sugar", "glucose syrup", "high fructose corn syrup", "corn syrup", "honey", "dextrose"]
_REFINED_CARB_KEYWORDS = ["maida", "refined wheat flour", "white flour"]
_TRANS_FAT_KEYWORDS = ["hydrogenated", "partially hydrogenated", "trans fat", "vanaspati"]
_GOITROGEN_KEYWORDS = ["soy", "soya", "cruciferous"]


class DiabetesRule(BaseRule):
    name = "diabetes"
    condition = RuleConditionKey.DIABETES

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        sugar_matches = any_ingredient_matches(context, _SUGAR_KEYWORDS)
        sugar_g = context.nutrition.sugar_g

        if sugar_g is not None and sugar_g >= 22.5:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.UNSAFE, RiskLevel.HIGH,
                [f"High sugar content ({sugar_g}g per serving).", "Unsafe for diabetes."],
                ["Choose a low-sugar or sugar-free alternative.", "Check for artificial sweeteners as a substitute."],
                sugar_matches,
            )
        if sugar_g is not None and sugar_g >= 10 or sugar_matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                ["Contains added sugar.", "Consume in moderation if diabetic."],
                ["Prefer whole-food snacks with lower glycemic impact."],
                sugar_matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class PrediabetesRule(BaseRule):
    name = "prediabetes"
    condition = RuleConditionKey.PREDIABETES

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        sugar_matches = any_ingredient_matches(context, _SUGAR_KEYWORDS)
        sugar_g = context.nutrition.sugar_g
        if (sugar_g is not None and sugar_g >= 15) or sugar_matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                ["Contains sugar - monitor intake to avoid progression to diabetes."],
                ["Limit frequency of consumption.", "Pair with fiber or protein to reduce glycemic impact."],
                sugar_matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class ObesityRule(BaseRule):
    name = "obesity"
    condition = RuleConditionKey.OBESITY

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        calories = context.nutrition.calories
        if calories is not None and calories >= 400:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                [f"High calorie content ({calories} kcal per serving)."],
                ["Choose a lower-calorie alternative.", "Watch portion size."],
                [],
            )
        return RuleResult.not_triggered(self.name, self.condition)


class HighCholesterolRule(BaseRule):
    name = "high_cholesterol"
    condition = RuleConditionKey.HIGH_CHOLESTEROL

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        fat_matches = any_ingredient_matches(context, _TRANS_FAT_KEYWORDS + ["palm oil", "butter", "ghee"])
        sat_fat = context.nutrition.saturated_fat_g

        trans_fat_hit = any_ingredient_matches(context, _TRANS_FAT_KEYWORDS)
        if trans_fat_hit:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.UNSAFE, RiskLevel.HIGH,
                ["Contains trans fat / hydrogenated oil.", "Unsafe for high cholesterol."],
                ["Avoid products with hydrogenated oils.", "Choose products using healthier oils (olive, canola)."],
                trans_fat_hit,
            )
        if (sat_fat is not None and sat_fat >= 5) or fat_matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                ["Contains saturated fat - limit intake with high cholesterol."],
                ["Prefer unsaturated fat sources.", "Check nutrition label for saturated fat per serving."],
                fat_matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class PcosRule(BaseRule):
    name = "pcos"
    condition = RuleConditionKey.PCOS

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        matches = any_ingredient_matches(context, _SUGAR_KEYWORDS + _REFINED_CARB_KEYWORDS)
        if matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                ["Contains refined sugar/carbohydrates - may worsen insulin resistance in PCOS."],
                ["Choose low-glycemic-index alternatives.", "Favor whole grains and fiber-rich foods."],
                matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class ThyroidRule(BaseRule):
    name = "thyroid"
    condition = RuleConditionKey.THYROID

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        matches = any_ingredient_matches(context, _GOITROGEN_KEYWORDS)
        if matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.LOW,
                ["Contains soy/goitrogenic ingredients - may interfere with thyroid function in large amounts."],
                ["Consume in moderation, away from thyroid medication timing."],
                matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)

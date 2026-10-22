from __future__ import annotations

from app.domain.enums import RiskLevel, RuleConditionKey, VerdictStatus
from app.infrastructure.medical_rules.rule_base import BaseRule, any_ingredient_matches
from app.infrastructure.medical_rules.rule_context import RuleContext, RuleResult

_PREGNANCY_UNSAFE_KEYWORDS = ["alcohol", "raw egg", "unpasteurized", "caffeine"]
_CHILD_CAUTION_KEYWORDS = ["artificial color", "caffeine", "high fructose corn syrup"]
_SUGAR_KEYWORDS = ["sugar", "glucose syrup", "high fructose corn syrup", "corn syrup", "honey"]
_PROTEIN_POSITIVE_HINT = ["protein", "whey", "casein", "soy protein"]

CHILD_AGE_THRESHOLD = 12


class PregnancyRule(BaseRule):
    name = "pregnancy"
    condition = RuleConditionKey.PREGNANCY

    def applies_to(self, context: RuleContext) -> bool:
        return bool(context.is_pregnant)

    def evaluate(self, context: RuleContext) -> RuleResult:
        matches = any_ingredient_matches(context, _PREGNANCY_UNSAFE_KEYWORDS)
        if matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.UNSAFE, RiskLevel.HIGH,
                ["This product may not be suitable because your profile indicates that you are pregnant.",
                 f"Pregnancy-relevant ingredient(s) detected: {', '.join(matches)}."],
                ["Avoid this product during pregnancy.", "Consult your doctor about dietary restrictions."],
                matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class ChildrenRule(BaseRule):
    name = "child"
    condition = RuleConditionKey.CHILD

    def applies_to(self, context: RuleContext) -> bool:
        return context.age is not None and context.age < CHILD_AGE_THRESHOLD

    def evaluate(self, context: RuleContext) -> RuleResult:
        matches = any_ingredient_matches(context, _CHILD_CAUTION_KEYWORDS)
        if matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                ["Contains artificial additives/caffeine - caution advised for children."],
                ["Prefer products with natural ingredients for children.", "Limit sugary snacks."],
                matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class WeightLossRule(BaseRule):
    name = "weight_loss"
    condition = RuleConditionKey.WEIGHT_LOSS

    def applies_to(self, context: RuleContext) -> bool:
        # Pregnancy guidance takes precedence over a stored weight-loss goal.
        # A historical scan retains the resulting profile snapshot and is never
        # recalculated if this setting changes later.
        return not context.is_pregnant and self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        calories = context.nutrition.calories
        sugar_matches = any_ingredient_matches(context, _SUGAR_KEYWORDS)
        if (calories is not None and calories >= 350) or sugar_matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.LOW,
                ["High calorie/sugar content relative to a weight-loss goal."],
                ["Choose a lower-calorie, high-protein alternative.", "Watch portion size."],
                sugar_matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class WeightGainRule(BaseRule):
    name = "weight_gain"
    condition = RuleConditionKey.WEIGHT_GAIN

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        protein_hint = any_ingredient_matches(context, _PROTEIN_POSITIVE_HINT)
        protein_g = context.nutrition.protein_g
        if protein_hint or (protein_g is not None and protein_g >= 10):
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.SAFE, RiskLevel.LOW,
                ["Good protein source - supports weight/muscle gain goals."],
                ["Pair with a calorie surplus and resistance training for best results."],
                protein_hint,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class SportsNutritionRule(BaseRule):
    name = "sports_nutrition"
    condition = RuleConditionKey.SPORTS_NUTRITION

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        protein_hint = any_ingredient_matches(context, _PROTEIN_POSITIVE_HINT)
        sugar_matches = any_ingredient_matches(context, _SUGAR_KEYWORDS)

        if protein_hint:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.SAFE, RiskLevel.LOW,
                ["Good protein source for sports nutrition."],
                ["Consume around workout windows for best recovery benefit."],
                protein_hint,
            )
        if sugar_matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.LOW,
                ["High in added sugar - fine for quick energy, not for sustained nutrition."],
                ["Best consumed immediately pre/post workout, not as a regular snack."],
                sugar_matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)

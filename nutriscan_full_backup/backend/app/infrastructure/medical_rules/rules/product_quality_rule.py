from __future__ import annotations

from app.domain.enums import RiskLevel, RuleConditionKey, VerdictStatus
from app.infrastructure.medical_rules.rule_base import BaseRule, any_ingredient_matches
from app.infrastructure.medical_rules.rule_context import RuleContext, RuleResult


# General per-serving nutrition thresholds.  They live with the reusable
# product-quality rules so every labelled product is evaluated consistently.
MODERATE_TOTAL_FAT_G = 10
SATURATED_FAT_G = 1.5
LOW_FIBER_G = 1
LOW_PROTEIN_G = 2


class ProductQualityRule(BaseRule):
    """Baseline label risks for every user, before profile-specific rules."""

    name = "product_quality"
    condition = RuleConditionKey.PRODUCT_QUALITY

    def applies_to(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> RuleResult:
        n = context.nutrition
        high_risk = any_ingredient_matches(context, ["partially hydrogenated", "hydrogenated oil"])
        moderate_risk = any_ingredient_matches(
            context, ["palm oil", "artificial colour", "artificial flavor", "flavour enhancer", "msg", "ins 621"]
        )
        if high_risk or (n.sugar_g is not None and n.sugar_g >= 25) or (n.sodium_mg is not None and n.sodium_mg >= 800):
            reasons = []
            if n.sugar_g is not None and n.sugar_g >= 25:
                reasons.append(f"High sugar content ({n.sugar_g:g}g per serving).")
            if n.sodium_mg is not None and n.sodium_mg >= 800:
                reasons.append(f"High sodium content ({n.sodium_mg:g}mg per serving).")
            if high_risk:
                reasons.append("Contains hydrogenated oil.")
            return RuleResult(self.name, self.condition, True, VerdictStatus.UNSAFE, RiskLevel.HIGH, reasons,
                              ["Choose a lower-sugar, lower-sodium minimally processed alternative."], high_risk)
        if moderate_risk or (n.sugar_g is not None and n.sugar_g >= 10) or (n.fat_g is not None and n.fat_g >= MODERATE_TOTAL_FAT_G):
            reasons = ["Contains processed ingredients that are best limited."] if moderate_risk else []
            factors = list(moderate_risk)
            if n.sugar_g is not None and n.sugar_g >= 10:
                reasons.append(f"Moderate sugar content ({n.sugar_g:g}g per serving).")
                factors.append("sugar")
            if n.fat_g is not None and n.fat_g >= MODERATE_TOTAL_FAT_G:
                reasons.append(f"High total fat for this serving ({n.fat_g:g}g).")
                factors.append("total fat")
            return RuleResult(self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE, reasons,
                              ["Prefer a minimally processed alternative for regular use."], list(dict.fromkeys(factors)))
        return RuleResult.not_triggered(self.name, self.condition)


class ProcessedSnackRule(BaseRule):
    """Uses the actual oil-and-salt label pattern for fried/processed snacks."""

    name = "processed_snack"
    condition = RuleConditionKey.PROCESSED_SNACK

    def applies_to(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> RuleResult:
        oil = any_ingredient_matches(context, ["vegetable oil", "sunflower oil", "corn oil", "canola oil"])
        salt = any_ingredient_matches(context, ["salt"])
        if not oil or not salt:
            return RuleResult.not_triggered(self.name, self.condition)
        return RuleResult(
            self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
            ["Processed snack profile: the label contains vegetable oil and salt."],
            ["Choose less frequently and pair snacks with a higher-fiber food."],
            list(dict.fromkeys(oil + salt + ["processed/fried snack profile"])),
        )


class LowNutrientDensityRule(BaseRule):
    """A serving-level nutrition rule with thresholds chosen for the label data.

    All four factors are required, preventing a low-protein or low-fiber food
    by itself from being labelled a concern.
    """

    name = "low_nutrient_density"
    condition = RuleConditionKey.LOW_NUTRIENT_DENSITY

    def applies_to(self, context: RuleContext) -> bool:
        return True

    def evaluate(self, context: RuleContext) -> RuleResult:
        n = context.nutrition
        is_profile = (
            n.fat_g is not None and n.fat_g >= MODERATE_TOTAL_FAT_G
            and n.saturated_fat_g is not None and n.saturated_fat_g >= SATURATED_FAT_G
            and n.fiber_g is not None and n.fiber_g <= LOW_FIBER_G
            and n.protein_g is not None and n.protein_g <= LOW_PROTEIN_G
        )
        if not is_profile:
            return RuleResult.not_triggered(self.name, self.condition)
        return RuleResult(
            self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
            ["This serving combines saturated fat with low dietary fiber and low protein."],
            ["For a regular snack, choose an option with more fiber and protein."],
            ["saturated fat", "low dietary fiber", "low protein"],
        )

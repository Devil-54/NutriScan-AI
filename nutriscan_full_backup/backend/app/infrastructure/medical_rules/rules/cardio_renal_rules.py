from __future__ import annotations

from app.domain.enums import RiskLevel, RuleConditionKey, VerdictStatus
from app.infrastructure.medical_rules.rule_base import BaseRule, any_ingredient_matches
from app.infrastructure.medical_rules.rule_context import RuleContext, RuleResult

_SODIUM_KEYWORDS = ["salt", "sodium", "msg", "monosodium glutamate", "baking soda", "sodium benzoate", "sodium phosphate"]
_TRANS_FAT_KEYWORDS = ["hydrogenated", "partially hydrogenated", "trans fat", "vanaspati", "palm oil"]
_KIDNEY_RISK_KEYWORDS = ["potassium chloride", "phosphoric acid", "sodium phosphate", "potassium sorbate"]
_LIVER_RISK_KEYWORDS = ["alcohol", "artificial color", "ins 102", "ins 110"]


class HypertensionRule(BaseRule):
    name = "hypertension"
    condition = RuleConditionKey.HYPERTENSION

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        sodium_matches = any_ingredient_matches(context, _SODIUM_KEYWORDS)
        sodium_mg = context.nutrition.sodium_mg

        if sodium_mg is not None and sodium_mg >= 800:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.UNSAFE, RiskLevel.HIGH,
                [f"High sodium content ({sodium_mg}mg per serving).", "Unsafe for hypertension."],
                ["Choose a low-sodium alternative.", "Avoid adding extra salt."],
                sodium_matches,
            )
        if (sodium_mg is not None and sodium_mg >= 400) or sodium_matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                ["Contains sodium/salt - monitor intake with hypertension."],
                ["Check the nutrition label for sodium per serving."],
                sodium_matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class HeartDiseaseRule(BaseRule):
    name = "heart_disease"
    condition = RuleConditionKey.HEART_DISEASE

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        trans_fat_matches = any_ingredient_matches(context, _TRANS_FAT_KEYWORDS)
        sodium_matches = any_ingredient_matches(context, _SODIUM_KEYWORDS)

        if trans_fat_matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.UNSAFE, RiskLevel.CRITICAL,
                ["Contains trans fat / hydrogenated oil.", "Unsafe for heart disease."],
                ["Avoid trans fats entirely.", "Choose products with healthier fat profiles."],
                trans_fat_matches,
            )
        if sodium_matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                ["Contains sodium - monitor intake for cardiovascular health."],
                ["Prefer low-sodium options."],
                sodium_matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class KidneyDiseaseRule(BaseRule):
    name = "kidney_disease"
    condition = RuleConditionKey.KIDNEY_DISEASE

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        matches = any_ingredient_matches(context, _KIDNEY_RISK_KEYWORDS + _SODIUM_KEYWORDS)
        sodium_mg = context.nutrition.sodium_mg

        if matches or (sodium_mg is not None and sodium_mg >= 400):
            severity_high = bool(any_ingredient_matches(context, _KIDNEY_RISK_KEYWORDS)) or (
                sodium_mg is not None and sodium_mg >= 800
            )
            return RuleResult(
                self.name, self.condition, True,
                VerdictStatus.UNSAFE if severity_high else VerdictStatus.WARNING,
                RiskLevel.HIGH if severity_high else RiskLevel.MODERATE,
                ["Contains phosphate/potassium/sodium additives.", "Caution advised for kidney disease."],
                ["Consult a renal dietitian before consuming.", "Choose products with minimal additives."],
                matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)


class LiverDiseaseRule(BaseRule):
    name = "liver_disease"
    condition = RuleConditionKey.LIVER_DISEASE

    def applies_to(self, context: RuleContext) -> bool:
        return self.condition in context.user_conditions

    def evaluate(self, context: RuleContext) -> RuleResult:
        matches = any_ingredient_matches(context, _LIVER_RISK_KEYWORDS)
        if matches:
            return RuleResult(
                self.name, self.condition, True, VerdictStatus.WARNING, RiskLevel.MODERATE,
                ["Contains additives/alcohol that may burden liver function."],
                ["Choose products with fewer artificial additives.", "Avoid alcohol-containing products entirely."],
                matches,
            )
        return RuleResult.not_triggered(self.name, self.condition)

from __future__ import annotations

from app.domain.enums import RiskLevel, RuleConditionKey, VerdictStatus
from app.infrastructure.medical_rules.rule_base import BaseRule
from app.infrastructure.medical_rules.rule_context import RuleContext, RuleResult


class AllergyRule(BaseRule):
    """
    Highest-priority rule: a confirmed allergen match is always UNSAFE /
    CRITICAL regardless of any other rule's verdict (see engine.py
    aggregation - critical allergy findings short-circuit to UNSAFE).
    """

    name = "food_allergy"
    condition = RuleConditionKey.FOOD_ALLERGY

    def applies_to(self, context: RuleContext) -> bool:
        return len(context.user_allergy_names) > 0

    def evaluate(self, context: RuleContext) -> RuleResult:
        user_allergies_lower = {a.lower() for a in context.user_allergy_names}

        matched: list[str] = []
        for allergen in context.allergen_names:
            if allergen.lower() in user_allergies_lower:
                matched.append(allergen)

        # Fallback: also check raw ingredient text for the allergy name itself
        # (covers the case where the Knowledge Graph hasn't linked this
        # ingredient to an allergen yet - text matching still works).
        for ingredient in context.ingredients:
            for allergy in context.user_allergy_names:
                key_terms = allergy.lower().replace(" protein", "").split()
                if any(term in ingredient.lower() for term in key_terms if len(term) > 3):
                    if allergy not in matched:
                        matched.append(allergy)

        if not matched:
            return RuleResult.not_triggered(self.name, self.condition)

        return RuleResult(
            rule_name=self.name,
            condition=self.condition,
            triggered=True,
            status=VerdictStatus.UNSAFE,
            risk_level=RiskLevel.CRITICAL,
            reasons=[f"Contains {m} allergen." for m in matched] + [f"Unsafe for {m} allergy." for m in matched],
            recommendations=["Avoid this product.", "Choose a product with a verified allergen-free label."],
            flagged_ingredients=matched,
        )

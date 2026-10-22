from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.enums import RuleConditionKey
from app.infrastructure.medical_rules.rule_context import RuleContext, RuleResult


class BaseRule(ABC):
    """
    One rule = one medical condition. `applies_to` decides relevance from
    the user's profile alone (cheap, no ingredient scanning); `evaluate` only
    runs for users the rule actually applies to. Add a new condition by
    subclassing this and registering it in engine.RULE_REGISTRY - nothing
    else in the engine needs to change.
    """

    name: str
    condition: RuleConditionKey

    @abstractmethod
    def applies_to(self, context: RuleContext) -> bool: ...

    @abstractmethod
    def evaluate(self, context: RuleContext) -> RuleResult: ...

    def run(self, context: RuleContext) -> RuleResult:
        if not self.applies_to(context):
            return RuleResult.not_triggered(self.name, self.condition)
        return self.evaluate(context)


def any_ingredient_matches(context: RuleContext, keywords: list[str]) -> list[str]:
    """Shared helper: returns which of the given keywords appear in any ingredient name.
    Works identically on raw parser text today and KG-enriched names later."""
    matches: list[str] = []
    lowered = context.ingredients_lower()
    for keyword in keywords:
        kw = keyword.lower()
        if any(kw in ingredient for ingredient in lowered):
            matches.append(keyword)
    return matches

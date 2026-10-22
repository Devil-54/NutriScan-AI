from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.enums import RiskLevel, RuleConditionKey, VerdictStatus


@dataclass
class NutritionSnapshot:
    """Optional product-level nutrition input. Any field may be None if not
    provided by the caller or not yet resolvable from the Knowledge Graph."""

    calories: float | None = None
    sugar_g: float | None = None
    sodium_mg: float | None = None
    fat_g: float | None = None
    saturated_fat_g: float | None = None
    protein_g: float | None = None
    fiber_g: float | None = None
    carbohydrates_g: float | None = None
    # Kept in the scan-time nutrition snapshot even though no current rule
    # uses them.  They are facts read from the label, not inferred values.
    trans_fat_g: float | None = None
    cholesterol_mg: float | None = None
    potassium_mg: float | None = None
    calcium_mg: float | None = None
    iron_mg: float | None = None


@dataclass
class RuleContext:
    """
    Everything a rule needs to evaluate a product against a user. Built once
    per evaluation by the use case and passed to every rule - rules never
    fetch data themselves, keeping them pure and independently testable.

    `ingredients` and `allergen_names` are plain strings so rules work
    identically whether they came from raw OCR/parser text (today) or an
    enriched Knowledge Graph lookup (once datasets are imported) - the rule
    interface never changes either way.
    """

    ingredients: list[str] = field(default_factory=list)
    allergen_names: list[str] = field(default_factory=list)
    additive_names: list[str] = field(default_factory=list)
    nutrition: NutritionSnapshot = field(default_factory=NutritionSnapshot)

    user_conditions: set[RuleConditionKey] = field(default_factory=set)
    user_allergy_names: set[str] = field(default_factory=set)
    age: int | None = None
    is_pregnant: bool | None = None

    def ingredients_lower(self) -> list[str]:
        return [i.lower() for i in self.ingredients]


@dataclass
class RuleResult:
    rule_name: str
    condition: RuleConditionKey
    triggered: bool
    status: VerdictStatus = VerdictStatus.SAFE
    risk_level: RiskLevel = RiskLevel.LOW
    reasons: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    flagged_ingredients: list[str] = field(default_factory=list)

    @staticmethod
    def not_triggered(rule_name: str, condition: RuleConditionKey) -> "RuleResult":
        return RuleResult(rule_name=rule_name, condition=condition, triggered=False)

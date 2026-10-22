from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.enums import RiskLevel, VerdictStatus
from app.infrastructure.medical_rules.rule_base import BaseRule
from app.infrastructure.medical_rules.rule_context import RuleContext, RuleResult
from app.infrastructure.medical_rules.rules.allergy_rule import AllergyRule
from app.infrastructure.medical_rules.rules.cardio_renal_rules import HeartDiseaseRule, HypertensionRule, KidneyDiseaseRule, LiverDiseaseRule
from app.infrastructure.medical_rules.rules.lifestyle_rules import ChildrenRule, PregnancyRule, SportsNutritionRule, WeightGainRule, WeightLossRule
from app.infrastructure.medical_rules.rules.metabolic_rules import DiabetesRule, HighCholesterolRule, ObesityRule, PcosRule, PrediabetesRule, ThyroidRule
from app.infrastructure.medical_rules.rules.product_quality_rule import (
    LowNutrientDensityRule,
    ProcessedSnackRule,
    ProductQualityRule,
)
from app.core.logging import get_logger

logger = get_logger()

# Add a new condition by instantiating its rule class here - nothing else changes.
RULE_REGISTRY: list[BaseRule] = [
    ProductQualityRule(),
    ProcessedSnackRule(),
    LowNutrientDensityRule(),
    AllergyRule(),
    DiabetesRule(),
    PrediabetesRule(),
    HypertensionRule(),
    HeartDiseaseRule(),
    KidneyDiseaseRule(),
    LiverDiseaseRule(),
    PregnancyRule(),
    ChildrenRule(),
    WeightLossRule(),
    WeightGainRule(),
    SportsNutritionRule(),
    HighCholesterolRule(),
    ObesityRule(),
    PcosRule(),
    ThyroidRule(),
]

_RISK_ORDER = {RiskLevel.LOW: 0, RiskLevel.MODERATE: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}
_STATUS_ORDER = {VerdictStatus.SAFE: 0, VerdictStatus.WARNING: 1, VerdictStatus.UNSAFE: 2}
_SEVERITY_SCORE_DEDUCTION = {RiskLevel.LOW: 5, RiskLevel.MODERATE: 12, RiskLevel.HIGH: 25, RiskLevel.CRITICAL: 45}


@dataclass
class EngineVerdict:
    status: VerdictStatus
    risk_level: RiskLevel
    severity: RiskLevel
    health_score: int
    reasons: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    safe_ingredients: list[str] = field(default_factory=list)
    unsafe_ingredients: list[str] = field(default_factory=list)
    triggered_rules: list[str] = field(default_factory=list)


class RuleEngine:
    def __init__(self, rules: list[BaseRule] | None = None) -> None:
        self.rules = rules if rules is not None else RULE_REGISTRY

    def evaluate(self, context: RuleContext) -> EngineVerdict:
        results: list[RuleResult] = []
        for rule in self.rules:
            try:
                results.append(rule.run(context))
            except Exception as exc:  # A single rule must never abandon a scan.
                logger.bind(event="MEDICAL_RULE_FAILED", rule=rule.name).exception(
                    "Medical rule failed; continuing with remaining rules"
                )
        triggered = [r for r in results if r.triggered]

        negative = [r for r in triggered if r.status in (VerdictStatus.WARNING, VerdictStatus.UNSAFE)]
        positive = [r for r in triggered if r.status == VerdictStatus.SAFE]

        if not negative:
            overall_status = VerdictStatus.SAFE
        else:
            overall_status = max((r.status for r in negative), key=lambda s: _STATUS_ORDER[s])

        risk_level = RiskLevel.LOW
        if negative:
            risk_level = max((r.risk_level for r in negative), key=lambda r: _RISK_ORDER[r])
        severity = risk_level

        score = 100
        for r in negative:
            score -= _SEVERITY_SCORE_DEDUCTION[r.risk_level]
        score = max(0, min(100, score))

        reasons: list[str] = []
        recommendations: list[str] = []
        unsafe_ingredients: list[str] = []
        for r in negative:
            reasons.extend(r.reasons)
            recommendations.extend(r.recommendations)
            unsafe_ingredients.extend(r.flagged_ingredients)
        for r in positive:
            reasons.extend(r.reasons)
            recommendations.extend(r.recommendations)

        unsafe_set = {i.lower() for i in unsafe_ingredients}
        safe_ingredients = [i for i in context.ingredients if i.lower() not in unsafe_set]

        return EngineVerdict(
            status=overall_status,
            risk_level=risk_level,
            severity=severity,
            health_score=score,
            reasons=list(dict.fromkeys(reasons)),
            recommendations=list(dict.fromkeys(recommendations)),
            safe_ingredients=safe_ingredients,
            unsafe_ingredients=list(dict.fromkeys(unsafe_ingredients)),
            triggered_rules=[r.rule_name for r in triggered],
        )

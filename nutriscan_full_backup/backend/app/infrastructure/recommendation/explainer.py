from __future__ import annotations

from abc import ABC, abstractmethod


class RecommendationExplainer(ABC):
    """
    Explanation-generation interface. `RuleBasedExplainer` is the only
    implementation today (deterministic templates - no external calls, per
    Phase 3G scope). A future `LlmExplainer` implementing this same
    interface (e.g. calling OpenAI/Groq/Gemini to rephrase these same
    facts more naturally) can be swapped in via the engine's constructor
    with zero changes to RecommendationEngine or any use case - mirrors the
    EmailService/VirusScanner pluggable-adapter pattern already used
    elsewhere in this codebase.
    """

    @abstractmethod
    def explain_unsafe_ingredient(self, ingredient: str, trigger_reasons: list[str]) -> str: ...

    @abstractmethod
    def explain_alternative(self, suggestion: str, trigger_category: str) -> str: ...


class RuleBasedExplainer(RecommendationExplainer):
    def explain_unsafe_ingredient(self, ingredient: str, trigger_reasons: list[str]) -> str:
        factor_explanations = {
            "vegetable oil": "Fat-related consideration from the scanned label.",
            "sunflower oil": "Fat-related consideration from the scanned label.",
            "corn oil": "Fat-related consideration from the scanned label.",
            "canola oil": "Fat-related consideration from the scanned label.",
            "salt": "Sodium-related consideration from the scanned label.",
            "processed/fried snack profile": "Dietary consideration based on the oil-and-salt snack profile.",
            "total fat": "Nutrition factor evaluated from the scanned-label serving value.",
            "saturated fat": "Nutrition factor evaluated from the scanned-label serving value.",
            "low dietary fiber": "Nutrition limitation evaluated from the scanned-label serving value.",
            "low protein": "Nutrition limitation evaluated from the scanned-label serving value.",
        }
        explanation = factor_explanations.get(ingredient.lower())
        if explanation:
            return explanation
        if trigger_reasons:
            return f"{ingredient} is not recommended because {trigger_reasons[0].rstrip('.').lower()}."
        return f"{ingredient} is not recommended based on your health profile."

    def explain_alternative(self, suggestion: str, trigger_category: str) -> str:
        category_phrases = {
            "sugar": "less sugar and a lower glycemic impact",
            "sodium": "less sodium",
            "trans_fat": "healthier fats and no hydrogenated oils",
            "saturated_fat": "less saturated fat",
            "refined_carb": "more fiber and whole grains",
            "allergen": "no known allergens for your profile",
            "calorie": "fewer calories per serving",
            "protein": "more protein per serving",
        }
        phrase = category_phrases.get(trigger_category, "a better overall nutrition profile")
        return f"{suggestion} is healthier because it likely contains {phrase}."

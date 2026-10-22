from __future__ import annotations

from app.domain.enums import RuleConditionKey

HEALTH_TIPS: dict[RuleConditionKey, list[str]] = {
    RuleConditionKey.DIABETES: ["Monitor total carbohydrate intake per meal.", "Prefer high-fiber, low-glycemic foods."],
    RuleConditionKey.PREDIABETES: ["Limit added sugar and refined carbs.", "Pair carbs with protein or fiber."],
    RuleConditionKey.HYPERTENSION: ["Keep sodium under 2000mg/day.", "Increase potassium-rich foods (bananas, spinach)."],
    RuleConditionKey.HEART_DISEASE: ["Avoid trans fats entirely.", "Favor unsaturated fats (olive oil, nuts)."],
    RuleConditionKey.KIDNEY_DISEASE: ["Limit phosphate and potassium additives.", "Consult a renal dietitian regularly."],
    RuleConditionKey.LIVER_DISEASE: ["Avoid alcohol and excess artificial additives.", "Favor whole, minimally processed foods."],
    RuleConditionKey.PREGNANCY: ["Avoid raw/unpasteurized ingredients and alcohol.", "Ensure adequate folate and iron intake."],
    RuleConditionKey.CHILD: ["Limit sugary snacks and artificial colors.", "Favor natural, whole-food snacks."],
    RuleConditionKey.WEIGHT_LOSS: ["Favor high-protein, high-fiber foods for satiety.", "Watch portion sizes and liquid calories."],
    RuleConditionKey.WEIGHT_GAIN: ["Add calorie-dense, nutrient-rich foods.", "Increase meal frequency."],
    RuleConditionKey.SPORTS_NUTRITION: ["Time protein intake around workouts.", "Stay hydrated with electrolytes during intense training."],
    RuleConditionKey.HIGH_CHOLESTEROL: ["Limit saturated and trans fat.", "Add soluble fiber (oats, legumes)."],
    RuleConditionKey.OBESITY: ["Focus on calorie density and portion control.", "Increase daily physical activity gradually."],
    RuleConditionKey.PCOS: ["Favor low-glycemic-index foods.", "Include regular physical activity to aid insulin sensitivity."],
    RuleConditionKey.THYROID: ["Limit excess soy/goitrogenic foods.", "Take medication separate from high-fiber or calcium-rich meals."],
}

NUTRITION_ADVICE: dict[RuleConditionKey, list[str]] = {
    RuleConditionKey.DIABETES: ["Target under 25g added sugar per day.", "Choose whole grains over refined grains."],
    RuleConditionKey.HYPERTENSION: ["Aim for under 1500-2000mg sodium/day.", "Read labels for hidden sodium (broths, sauces)."],
    RuleConditionKey.KIDNEY_DISEASE: ["Discuss protein targets with your care team.", "Watch phosphorus additives in processed foods."],
    RuleConditionKey.PREGNANCY: ["Increase folate, iron, and calcium intake.", "Avoid excess caffeine (under 200mg/day)."],
    RuleConditionKey.WEIGHT_LOSS: ["Create a moderate calorie deficit, not extreme.", "Prioritize protein to preserve muscle mass."],
    RuleConditionKey.WEIGHT_GAIN: ["Aim for a calorie surplus with nutrient-dense foods.", "Include healthy fats (nuts, avocado)."],
    RuleConditionKey.SPORTS_NUTRITION: ["Consume 1.2-2.0g protein/kg body weight if active.", "Replenish carbs after intense training."],
    RuleConditionKey.HIGH_CHOLESTEROL: ["Limit saturated fat to under 6% of calories.", "Increase omega-3 rich foods (fish, flax)."],
}

LIFESTYLE_ADVICE: dict[RuleConditionKey, list[str]] = {
    RuleConditionKey.WEIGHT_LOSS: ["Combine diet changes with 150+ min/week moderate exercise."],
    RuleConditionKey.WEIGHT_GAIN: ["Pair extra calories with resistance training for muscle gain."],
    RuleConditionKey.SPORTS_NUTRITION: ["Prioritize sleep and recovery alongside nutrition."],
    RuleConditionKey.HYPERTENSION: ["Regular moderate cardio helps lower blood pressure over time."],
    RuleConditionKey.DIABETES: ["Regular physical activity improves insulin sensitivity."],
    RuleConditionKey.PREGNANCY: ["Consult your obstetrician before starting any new exercise routine."],
    RuleConditionKey.PCOS: ["Regular exercise helps manage insulin resistance in PCOS."],
}

GENERIC_HEALTH_TIP = "Read ingredient labels carefully and favor minimally processed foods."
GENERIC_LIFESTYLE_TIP = "Maintain regular physical activity and balanced meals."

# Trigger category -> alternative suggestions (matches the spec's "High Sugar -> ..." example).
ALTERNATIVE_TEMPLATES: dict[str, list[str]] = {
    "sugar": ["Sugar-free alternatives", "Whole grain alternatives", "Healthy snacks with natural sweetness (fruit)"],
    "sodium": ["Low-sodium alternatives", "Fresh/unprocessed versions of this food", "Herb-seasoned alternatives"],
    "trans_fat": ["Products using olive/canola oil instead", "Non-hydrogenated snack alternatives"],
    "saturated_fat": ["Lean protein alternatives", "Plant-based fat alternatives"],
    "refined_carb": ["Whole grain alternatives", "High-fiber alternatives"],
    "allergen": ["Certified allergen-free alternatives", "Products with a verified 'free-from' label"],
    "calorie": ["Lower-calorie portion alternatives", "Nutrient-dense, lower-calorie snacks"],
    "protein": ["Higher-protein alternatives", "Protein-fortified versions of this food"],
}

_TRIGGER_KEYWORDS: dict[str, list[str]] = {
    "sugar": ["sugar", "glucose", "fructose", "syrup", "honey", "dextrose"],
    "sodium": ["sodium", "salt"],
    "trans_fat": ["trans fat", "hydrogenated", "vanaspati"],
    "saturated_fat": ["saturated fat", "palm oil", "butter", "ghee"],
    "refined_carb": ["maida", "refined wheat", "white flour"],
    "allergen": ["allergen", "allergy"],
    "calorie": ["calorie"],
    "protein": ["protein"],
}


def detect_trigger_categories(reasons: list[str]) -> list[str]:
    """Lightweight keyword scan over rule-engine reason text to pick which
    alternative-suggestion category applies - avoids needing to modify
    Phase 3F's RuleResult/EngineVerdict shape to carry structured trigger
    metadata."""
    text = " ".join(reasons).lower()
    return [cat for cat, keywords in _TRIGGER_KEYWORDS.items() if any(kw in text for kw in keywords)]

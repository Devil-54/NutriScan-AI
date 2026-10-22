/// Dummy Result-screen data only (Phase 4E scope) - no backend types here.
library;

enum IngredientStatus { safe, warning, danger }

enum RiskLevel { safe, lowRisk, moderateRisk, highRisk, unsafe }

extension RiskLevelLabel on RiskLevel {
  String get label => switch (this) {
        RiskLevel.safe => 'Safe',
        RiskLevel.lowRisk => 'Low Risk',
        RiskLevel.moderateRisk => 'Moderate Risk',
        RiskLevel.highRisk => 'High Risk',
        RiskLevel.unsafe => 'Unsafe',
      };
}

class IngredientResult {
  const IngredientResult({required this.name, required this.status, required this.explanation});
  final String name;
  final IngredientStatus status;
  final String explanation;
}

class NutritionFact {
  const NutritionFact({required this.label, required this.value, required this.unit, required this.emoji});
  final String label;
  final String value;
  final String unit;
  final String emoji;
}

class AdditiveResult {
  const AdditiveResult({
    required this.insNumber,
    required this.purpose,
    required this.riskLevel,
    required this.explanation,
  });
  final String insNumber;
  final String purpose;
  final String riskLevel;
  final String explanation;
}

class AlternativeFood {
  const AlternativeFood({required this.name, required this.emoji});
  final String name;
  final String emoji;
}

// ---- Dummy dataset for a sample scanned product ----

const dummyProductName = 'Maggi Noodles';
const dummyHealthScore = 82;
const dummyRiskLevel = RiskLevel.moderateRisk;

const dummyIngredientResults = [
  IngredientResult(name: 'Refined Wheat Flour', status: IngredientStatus.warning, explanation: 'Low fiber, high glycemic index.'),
  IngredientResult(name: 'Palm Oil', status: IngredientStatus.warning, explanation: 'High in saturated fat.'),
  IngredientResult(name: 'Salt', status: IngredientStatus.safe, explanation: 'Within normal range for this serving.'),
  IngredientResult(name: 'INS 621 (MSG)', status: IngredientStatus.danger, explanation: 'Flavor enhancer linked to sensitivity in some people.'),
  IngredientResult(name: 'Onion Powder', status: IngredientStatus.safe, explanation: 'No known risk for your profile.'),
];

const dummyNutritionFacts = [
  NutritionFact(label: 'Calories', value: '350', unit: 'kcal', emoji: '🔥'),
  NutritionFact(label: 'Protein', value: '7', unit: 'g', emoji: '💪'),
  NutritionFact(label: 'Sugar', value: '2', unit: 'g', emoji: '🍬'),
  NutritionFact(label: 'Fat', value: '14', unit: 'g', emoji: '🧈'),
  NutritionFact(label: 'Fiber', value: '2', unit: 'g', emoji: '🌾'),
  NutritionFact(label: 'Sodium', value: '900', unit: 'mg', emoji: '🧂'),
];

const dummyDetectedAllergens = ['Gluten', 'Soy'];
const dummyAllAllergensChecked = ['Milk', 'Soy', 'Gluten', 'Tree Nuts', 'Egg'];

const dummyAdditives = [
  AdditiveResult(
    insNumber: 'INS 621',
    purpose: 'Flavor Enhancer',
    riskLevel: 'Moderate',
    explanation: 'Monosodium glutamate - generally recognized as safe, but some people report sensitivity.',
  ),
  AdditiveResult(
    insNumber: 'INS 508',
    purpose: 'Firming Agent',
    riskLevel: 'Low',
    explanation: 'Potassium chloride - used to retain texture, low risk for most people.',
  ),
];

const dummyAiRecommendation =
    'Suitable occasionally, not for regular consumption. Good for active adults with no sodium-sensitive '
    'conditions. Not recommended for individuals managing diabetes or hypertension.';

const dummyReasons = ['High Sodium', 'Contains Preservatives', 'Low Fiber', 'Contains Artificial Flavoring'];

const dummyAlternatives = [
  AlternativeFood(name: 'Roasted Makhana', emoji: '🌰'),
  AlternativeFood(name: 'Whole Wheat Crackers', emoji: '🍘'),
  AlternativeFood(name: 'Mixed Nuts', emoji: '🥜'),
  AlternativeFood(name: 'Fresh Fruits', emoji: '🍎'),
  AlternativeFood(name: 'Oats Cookies', emoji: '🍪'),
];

const dummyHealthTip = 'Reduce sodium intake for the rest of today - this product covers 38% of your daily limit.';

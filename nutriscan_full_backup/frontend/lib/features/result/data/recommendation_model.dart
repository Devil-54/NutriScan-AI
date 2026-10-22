class AlternativeItemModel {
  const AlternativeItemModel({required this.suggestion, required this.reason});
  final String suggestion;
  final String reason;

  factory AlternativeItemModel.fromJson(Map<String, dynamic> json) =>
      AlternativeItemModel(suggestion: json['suggestion'] as String, reason: json['reason'] as String);
}

class IngredientWarningModel {
  const IngredientWarningModel({required this.ingredient, required this.reason});
  final String ingredient;
  final String reason;

  factory IngredientWarningModel.fromJson(Map<String, dynamic> json) =>
      IngredientWarningModel(ingredient: json['ingredient'] as String, reason: json['reason'] as String);
}

class RecommendationResultModel {
  const RecommendationResultModel({
    required this.status,
    required this.riskLevel,
    required this.safeFoods,
    required this.unsafeFoods,
    required this.alternatives,
    required this.healthTips,
    required this.nutritionAdvice,
    required this.lifestyleAdvice,
    required this.ingredientWarnings,
    required this.recommendationScore,
    required this.confidenceScore,
    required this.reasons,
  });

  final String status;
  final String riskLevel;
  final List<String> safeFoods;
  final List<String> unsafeFoods;
  final List<AlternativeItemModel> alternatives;
  final List<String> healthTips;
  final List<String> nutritionAdvice;
  final List<String> lifestyleAdvice;
  final List<IngredientWarningModel> ingredientWarnings;
  final int recommendationScore;
  final int confidenceScore;
  final List<String> reasons;

  factory RecommendationResultModel.fromJson(Map<String, dynamic> json) => RecommendationResultModel(
        status: json['status'] as String,
        riskLevel: json['risk_level'] as String,
        safeFoods: (json['safe_foods'] as List).cast<String>(),
        unsafeFoods: (json['unsafe_foods'] as List).cast<String>(),
        alternatives: (json['alternatives'] as List)
            .map((e) => AlternativeItemModel.fromJson(e as Map<String, dynamic>))
            .toList(),
        healthTips: (json['health_tips'] as List).cast<String>(),
        nutritionAdvice: (json['nutrition_advice'] as List).cast<String>(),
        lifestyleAdvice: (json['lifestyle_advice'] as List).cast<String>(),
        ingredientWarnings: (json['ingredient_warnings'] as List)
            .map((e) => IngredientWarningModel.fromJson(e as Map<String, dynamic>))
            .toList(),
        recommendationScore: json['recommendation_score'] as int,
        confidenceScore: json['confidence_score'] as int,
        reasons: (json['reasons'] as List).cast<String>(),
      );
}

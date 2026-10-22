class NutritionSummaryModel {
  const NutritionSummaryModel({
    this.calories,
    this.proteinG,
    this.sugarG,
    this.fatG,
    this.sodiumMg,
    this.carbohydratesG,
  });

  final double? calories;
  final double? proteinG;
  final double? sugarG;
  final double? fatG;
  final double? sodiumMg;
  final double? carbohydratesG;

  factory NutritionSummaryModel.fromJson(Map<String, dynamic>? json) =>
      NutritionSummaryModel(
        calories: (json?['calories'] as num?)?.toDouble(),
        proteinG: (json?['protein_g'] as num?)?.toDouble(),
        sugarG: (json?['sugar_g'] as num?)?.toDouble(),
        fatG: (json?['fat_g'] as num?)?.toDouble(),
        sodiumMg: (json?['sodium_mg'] as num?)?.toDouble(),
        carbohydratesG: (json?['carbohydrates_g'] as num?)?.toDouble(),
      );
}

class ScanAnalysisPayload {
  const ScanAnalysisPayload({
    required this.scanId,
    required this.ocrText,
    required this.scanTime,
    this.productName,
    this.brand,
    this.category,
    this.nutrition,
  });

  final String scanId;
  final String ocrText;
  final DateTime scanTime;
  final String? productName;
  final String? brand;
  final String? category;
  final NutritionSummaryModel? nutrition;
}

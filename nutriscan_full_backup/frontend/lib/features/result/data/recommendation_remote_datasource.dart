import '../../../core/services/api_service.dart';
import 'recommendation_model.dart';
import 'scan_analysis_payload.dart';

class RecommendationRemoteDatasource {
  RecommendationRemoteDatasource(this._api);
  final ApiService _api;

  Future<RecommendationResultModel> generate(
    List<String> ingredients, {
    required String scanId,
    String? productName,
    NutritionSummaryModel? nutrition,
  }) async {
    final res = await _api.post('/recommendation/generate', data: {
      'ingredients': ingredients,
      'scan_id': scanId,
      if (productName?.trim().isNotEmpty == true) 'product_name': productName,
      if (nutrition != null) 'nutrition': {
        'calories': nutrition.calories,
        'protein_g': nutrition.proteinG,
        'sugar_g': nutrition.sugarG,
        'fat_g': nutrition.fatG,
        'sodium_mg': nutrition.sodiumMg,
        'carbohydrates_g': nutrition.carbohydratesG,
      },
    });
    return RecommendationResultModel.fromJson(res['data'] as Map<String, dynamic>);
  }

  Future<List<Map<String, dynamic>>> history({int page = 1, int limit = 20}) async {
    final res = await _api.get('/recommendation/history', query: {'page': page, 'limit': limit});
    return (res['data'] as List).cast<Map<String, dynamic>>();
  }
}

import 'recommendation_model.dart';
import 'recommendation_remote_datasource.dart';
import 'scan_analysis_payload.dart';

class RecommendationRepository {
  RecommendationRepository(this._remote);
  final RecommendationRemoteDatasource _remote;

  Future<RecommendationResultModel> generate(
    List<String> ingredients, {
    required String scanId,
    String? productName,
    NutritionSummaryModel? nutrition,
  }) => _remote.generate(
        ingredients,
        scanId: scanId,
        productName: productName,
        nutrition: nutrition,
      );

  Future<List<Map<String, dynamic>>> history({int page = 1, int limit = 20}) =>
      _remote.history(page: page, limit: limit);
}

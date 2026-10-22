import '../../../core/network/api_exception.dart';
import '../../../core/services/api_service.dart';
import 'scan_analysis_payload.dart';

class OcrResultModel {
  const OcrResultModel({
    required this.ingredientsText,
    required this.confidence,
    required this.engine,
    this.productName,
    this.brand,
    this.category,
    this.nutrition,
  });
  final String ingredientsText;
  final double confidence;
  final String engine;
  final String? productName;
  final String? brand;
  final String? category;
  final NutritionSummaryModel? nutrition;

  factory OcrResultModel.fromJson(Map<String, dynamic> json) => OcrResultModel(
        ingredientsText: json['ingredients_text'] as String? ?? '',
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
        engine: json['engine'] as String? ?? '',
        productName: json['product_name'] as String?,
        brand: json['brand'] as String?,
        category: json['category'] as String?,
        nutrition: json['nutrition'] is Map<String, dynamic>
            ? NutritionSummaryModel.fromJson(
                json['nutrition'] as Map<String, dynamic>)
            : null,
      );
}

class OcrRemoteDatasource {
  OcrRemoteDatasource(this._api);
  final ApiService _api;

  /// scan_id is a query param on this endpoint, not a body field.
  Future<OcrResultModel> process(String scanId) async {
    try {
      // OCR can legitimately take longer than ordinary JSON calls on a
      // high-resolution label.  It still has a finite timeout and surfaces a
      // retryable error instead of leaving the progress screen stuck.
      final res = await _api.post(
        '/ocr/process?scan_id=$scanId',
        receiveTimeout: const Duration(seconds: 90),
      );
      return OcrResultModel.fromJson(res['data'] as Map<String, dynamic>);
    } on ValidationApiException catch (e) {
      if (e.code == 'OCR_ALREADY_PROCESSED') {
        return getResult(scanId);
      }
      rethrow;
    }
  }

  Future<OcrResultModel> getResult(String scanId) async {
    final res = await _api.get('/ocr/result/$scanId');
    return OcrResultModel.fromJson(res['data'] as Map<String, dynamic>);
  }
}

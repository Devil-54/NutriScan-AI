import '../../../core/services/api_service.dart';

class ParserRemoteDatasource {
  ParserRemoteDatasource(this._api);
  final ApiService _api;

  Future<List<String>> parseIngredients(String ocrText) async {
    final res = await _api.post('/parser/ingredients', data: {'ocr_text': ocrText});
    final data = res['data'] as Map<String, dynamic>;
    return (data['ingredients'] as List).cast<String>();
  }
}

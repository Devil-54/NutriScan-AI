import '../../../core/network/api_exception.dart';
import '../../../core/services/api_service.dart';

class ScanRemoteDatasource {
  ScanRemoteDatasource(this._api);
  final ApiService _api;

  /// Returns the created scan_id.
  Future<String> uploadScan(String filePath, {void Function(int sent, int total)? onProgress}) async {
    try {
      final res = await _api.uploadFile('/scans/upload', filePath, onProgress: onProgress);
      final data = res['data'] as Map<String, dynamic>;
      return data['scan_id'] as String;
    } on ConflictException catch (error) {
      if (error.code == 'DUPLICATE_UPLOAD') {
        final match = RegExp(
          r'scan_id=([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})',
        ).firstMatch(error.message);
        if (match != null) return match.group(1)!;
      }
      rethrow;
    }
  }
}

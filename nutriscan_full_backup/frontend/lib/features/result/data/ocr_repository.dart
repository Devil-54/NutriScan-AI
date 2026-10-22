import 'ocr_remote_datasource.dart';

class OcrRepository {
  OcrRepository(this._remote);
  final OcrRemoteDatasource _remote;

  Future<OcrResultModel> process(String scanId) => _remote.process(scanId);

  Future<OcrResultModel> getResult(String scanId) => _remote.getResult(scanId);
}

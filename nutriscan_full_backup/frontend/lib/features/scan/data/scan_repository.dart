import 'scan_remote_datasource.dart';

class ScanRepository {
  ScanRepository(this._remote);
  final ScanRemoteDatasource _remote;

  Future<String> uploadScan(String filePath, {void Function(int sent, int total)? onProgress}) =>
      _remote.uploadScan(filePath, onProgress: onProgress);
}

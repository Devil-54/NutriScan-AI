import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/services/api_service.dart';
import '../../data/scan_remote_datasource.dart';
import '../../data/scan_repository.dart';

final scanRepositoryProvider = Provider<ScanRepository>((ref) {
  return ScanRepository(ScanRemoteDatasource(ref.watch(apiServiceProvider)));
});

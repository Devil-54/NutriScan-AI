import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/services/api_service.dart';
import '../../../authentication/presentation/providers/auth_provider.dart';

/// Scans are created by the upload pipeline, so history must read the scan
/// records themselves rather than unrelated recommendation evaluations.
final scanHistoryProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  // Indexed shell branches can be created while the session is still being
  // restored.  Depend on auth so an early unauthenticated request is never
  // cached as this user's permanently-empty history.
  final auth = ref.watch(authProvider);
  if (auth.isLoading || auth.valueOrNull == null) return const [];

  // Do not include tokens or OCR text in logs.  These messages are useful
  final response = await ref.watch(apiServiceProvider)
      .get('/scans/history', query: {'page': 1, 'limit': 50});
  final data = response['data'];
  if (data is! List) {
    throw const FormatException('Invalid scan history response.');
  }
  final records = data
      .whereType<Map>()
      .map((item) => Map<String, dynamic>.from(item))
      .toList(growable: false);
  return records;
});

/// Detail is reloaded by ID so the view always represents the selected,
/// server-authorized record rather than a generic or stale list item.
final scanDetailProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, scanId) async {
  if (scanId.isEmpty) throw const FormatException('Missing scan ID.');
  final response = await ref.watch(apiServiceProvider).get('/scans/$scanId');
  final data = response['data'];
  if (data is! Map) throw const FormatException('Invalid scan detail response.');
  return Map<String, dynamic>.from(data);
});

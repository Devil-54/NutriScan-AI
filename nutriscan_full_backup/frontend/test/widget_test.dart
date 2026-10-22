import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:nutriscan_app/core/services/api_service.dart';
import 'package:nutriscan_app/core/services/secure_storage_service.dart';
import 'package:nutriscan_app/core/services/storage_service.dart';
import 'package:nutriscan_app/main.dart';

/// In-memory stand-in for SecureStorageService - avoids touching the real
/// flutter_secure_storage platform channel, which isn't available under
/// the default flutter_test binding.
class _FakeSecureStorageService extends SecureStorageService {
  final _values = <String, String>{};

  @override
  Future<String?> getString(String key) async => _values[key];

  @override
  Future<void> setString(String key, String value) async => _values[key] = value;

  @override
  Future<void> remove(String key) async => _values.remove(key);

  @override
  Future<void> clear() async => _values.clear();
}

void main() {
  testWidgets('App boots and renders the splash screen', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    final storage = StorageService(prefs);
    final secureStorage = _FakeSecureStorageService();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          storageServiceProvider.overrideWithValue(storage),
          secureStorageServiceProvider.overrideWithValue(secureStorage),
          // No stored token -> authProvider resolves to null without a
          // real network call, so the router's redirect logic can run.
          apiServiceProvider.overrideWithValue(ApiService(storage: secureStorage)),
        ],
        child: const NutriScanApp(),
      ),
    );
    // Advance through the splash entrance animations but stay before the
    // delayed route transition, so the splash remains on screen.
    await tester.pump(const Duration(seconds: 1));

    expect(find.text('NutriScan'), findsOneWidget);
    expect(find.text('AI Powered Food Safety'), findsOneWidget);
  });
}

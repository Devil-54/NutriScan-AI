import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Encrypted key-value storage for sensitive values only (access/refresh
/// JWTs). Non-sensitive prefs (theme, onboarding flags) stay in
/// [StorageService]/SharedPreferences - no need to pay the platform-channel
/// cost of secure storage for those. Unlike SharedPreferences, there is no
/// synchronous read API here; every read is a real async platform call.
class SecureStorageService {
  SecureStorageService({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
            );

  final FlutterSecureStorage _storage;

  Future<void> setString(String key, String value) => _storage.write(key: key, value: value);
  Future<String?> getString(String key) => _storage.read(key: key);
  Future<void> remove(String key) => _storage.delete(key: key);
  Future<void> clear() => _storage.deleteAll();
}

/// Overridden in main() - see main.dart. Unlike storageServiceProvider,
/// this doesn't need an async instance (FlutterSecureStorage has no
/// awaited factory), but is still injected for testability/consistency.
final secureStorageServiceProvider = Provider<SecureStorageService>((ref) {
  throw UnimplementedError('secureStorageServiceProvider must be overridden in main()');
});

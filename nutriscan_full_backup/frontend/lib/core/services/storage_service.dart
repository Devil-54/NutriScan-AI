import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Thin wrapper around SharedPreferences for simple key-value persistence
/// (tokens, theme preference, onboarding flags). Kept generic/reusable -
/// feature-specific storage logic (e.g. caching scan history) belongs in
/// each feature's own data layer, not here.
class StorageService {
  StorageService(this._prefs);

  final SharedPreferences _prefs;

  Future<bool> setString(String key, String value) => _prefs.setString(key, value);
  String? getString(String key) => _prefs.getString(key);

  Future<bool> setBool(String key, bool value) => _prefs.setBool(key, value);
  bool? getBool(String key) => _prefs.getBool(key);

  Future<bool> remove(String key) => _prefs.remove(key);
  Future<bool> clear() => _prefs.clear();
}

/// Overridden in main() with the resolved SharedPreferences instance before
/// runApp() - see main.dart. Throws if read before that override is applied,
/// which is intentional (fail fast on a genuine startup-order bug).
final storageServiceProvider = Provider<StorageService>((ref) {
  throw UnimplementedError('storageServiceProvider must be overridden in main()');
});

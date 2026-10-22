import '../../../core/constants/app_constants.dart';
import '../../../core/services/secure_storage_service.dart';
import 'auth_remote_datasource.dart';
import 'user_model.dart';

class AuthRepository {
  AuthRepository(this._remote, this._storage);
  final AuthRemoteDatasource _remote;
  final SecureStorageService _storage;

  /// Async because SecureStorageService (flutter_secure_storage) has no
  /// synchronous read API - callers must await this now.
  Future<bool> get isLoggedIn async => await _storage.getString(AppConstants.keyAccessToken) != null;

  Future<void> register({required String name, required String email, required String password}) =>
      _remote.register(name: name, email: email, password: password);

  Future<void> login({required String email, required String password}) async {
    final (access, refresh) = await _remote.login(email: email, password: password);
    await _storage.setString(AppConstants.keyAccessToken, access);
    await _storage.setString(AppConstants.keyRefreshToken, refresh);
  }

  Future<void> logout() async {
    final refresh = await _storage.getString(AppConstants.keyRefreshToken);
    try {
      if (refresh != null) await _remote.logout(refresh);
    } finally {
      await _storage.remove(AppConstants.keyAccessToken);
      await _storage.remove(AppConstants.keyRefreshToken);
    }
  }

  Future<void> forgotPassword(String email) => _remote.forgotPassword(email);

  Future<UserModel> getCurrentUser() => _remote.getCurrentUser();
}

import '../../../core/services/api_service.dart';
import 'user_model.dart';

class AuthRemoteDatasource {
  AuthRemoteDatasource(this._api);
  final ApiService _api;

  Future<void> register({required String name, required String email, required String password}) async {
    await _api.post('/auth/register', data: {'name': name, 'email': email, 'password': password});
  }

  /// Returns (accessToken, refreshToken).
  Future<(String, String)> login({required String email, required String password}) async {
    final res = await _api.post('/auth/login', data: {'email': email, 'password': password});
    final data = res['data'] as Map<String, dynamic>;
    return (data['access_token'] as String, data['refresh_token'] as String);
  }

  Future<void> logout(String refreshToken) async {
    await _api.post('/auth/logout', data: {'refresh_token': refreshToken});
  }

  Future<void> forgotPassword(String email) async {
    await _api.post('/auth/forgot-password', data: {'email': email});
  }

  Future<UserModel> getCurrentUser() async {
    final res = await _api.get('/users/me');
    return UserModel.fromJson(res['data'] as Map<String, dynamic>);
  }
}

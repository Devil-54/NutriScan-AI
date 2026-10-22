import 'package:dio/dio.dart';

import '../constants/app_constants.dart';
import '../services/secure_storage_service.dart';

/// Refresh-on-401 uses a bare Dio (no interceptors) to call /auth/refresh,
/// avoiding recursive interceptor loops. [onSessionExpired] is invoked when
/// refresh itself fails, so the caller (auth provider) can clear state and
/// route to Login - this interceptor has no Riverpod access of its own.
///
/// Tokens live in [SecureStorageService] (flutter_secure_storage), which has
/// no synchronous read API, so onRequest/onError are async here - Dio
/// tolerates this since it only requires handler.next/resolve/reject to be
/// called eventually, not synchronously.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required this.storage,
    required this.refreshDio,
    required this.baseUrl,
    required this.onSessionExpired,
  });

  final SecureStorageService storage;
  final Dio refreshDio;
  final String baseUrl;
  final void Function() onSessionExpired;

  bool _isRefreshing = false;

  static const _publicAuthPaths = <String>{
    '/auth/register',
    '/auth/login',
    '/auth/refresh',
    '/auth/forgot-password',
    '/auth/reset-password',
    '/auth/verify-email',
  };

  bool _isPublicAuthPath(String path) =>
      _publicAuthPaths.any((endpoint) => path.endsWith(endpoint));

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (!_isPublicAuthPath(options.path)) {
      final token = await storage.getString(AppConstants.keyAccessToken);
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    handler.next(options);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final isPublicAuthEndpoint = _isPublicAuthPath(err.requestOptions.path);
    if (err.response?.statusCode != 401 || isPublicAuthEndpoint || _isRefreshing) {
      handler.next(err);
      return;
    }

    final refreshToken = await storage.getString(AppConstants.keyRefreshToken);
    if (refreshToken == null) {
      onSessionExpired();
      handler.next(err);
      return;
    }

    _isRefreshing = true;
    try {
      final response = await refreshDio.post(
        '$baseUrl/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      final data = response.data['data'] as Map;
      await storage.setString(AppConstants.keyAccessToken, data['access_token'] as String);
      await storage.setString(AppConstants.keyRefreshToken, data['refresh_token'] as String);

      final retryOptions = err.requestOptions;
      retryOptions.headers['Authorization'] = 'Bearer ${data['access_token']}';
      final retryResponse = await refreshDio.fetch(retryOptions);
      handler.resolve(retryResponse);
    } catch (_) {
      await storage.remove(AppConstants.keyAccessToken);
      await storage.remove(AppConstants.keyRefreshToken);
      onSessionExpired();
      handler.next(err);
    } finally {
      _isRefreshing = false;
    }
  }
}

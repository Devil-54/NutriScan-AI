import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/app_config.dart';
import '../network/auth_interceptor.dart';
import '../network/dio_error_mapper.dart';
import 'secure_storage_service.dart';

/// Thin wrapper around a configured Dio instance with auth attachment,
/// 401-refresh, typed error mapping, and one retry for GET timeouts.
/// Feature repositories inject this via [apiServiceProvider] and call
/// get/post/put/patch/delete/upload - never raw Dio - so error handling
/// stays centralized instead of duplicated per repository.
class ApiService {
  ApiService({required SecureStorageService storage, void Function()? onSessionExpired})
      : _storage = storage,
        _dio = Dio(
          BaseOptions(
            baseUrl: AppConfig.apiBaseUrl,
            connectTimeout: AppConfig.connectTimeout,
            receiveTimeout: AppConfig.receiveTimeout,
            headers: {'Content-Type': 'application/json'},
          ),
        ) {
    _dio.interceptors.add(
      AuthInterceptor(
        storage: _storage,
        refreshDio: Dio(BaseOptions(headers: {'Content-Type': 'application/json'})),
        baseUrl: AppConfig.apiBaseUrl,
        onSessionExpired: onSessionExpired ?? () {},
      ),
    );
  }

  final SecureStorageService _storage;
  final Dio _dio;

  Dio get client => _dio;

  Future<Map<String, dynamic>> get(String path, {Map<String, dynamic>? query}) => _getWithRetry(path, query: query);

  Future<Map<String, dynamic>> _getWithRetry(String path, {Map<String, dynamic>? query, bool retried = false}) async {
    try {
      final response = await _dio.get(path, queryParameters: query);
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      if (!retried && _isRetryableTimeout(e)) {
        return _getWithRetry(path, query: query, retried: true);
      }
      throw mapDioException(e);
    }
  }

  Future<Map<String, dynamic>> post(String path, {Object? data, Duration? receiveTimeout}) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        options: receiveTimeout == null ? null : Options(receiveTimeout: receiveTimeout),
      );
      final responseData = response.data;
      return responseData == null
          ? <String, dynamic>{}
          : responseData as Map<String, dynamic>;
    } on DioException catch (e) {
      throw mapDioException(e);
    }
  }

  Future<Map<String, dynamic>> put(String path, {Object? data}) async {
    try {
      final response = await _dio.put(path, data: data);
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw mapDioException(e);
    }
  }

  Future<Map<String, dynamic>> patch(String path, {Object? data}) async {
    try {
      final response = await _dio.patch(path, data: data);
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw mapDioException(e);
    }
  }

  Future<void> delete(String path) async {
    try {
      await _dio.delete(path);
    } on DioException catch (e) {
      throw mapDioException(e);
    }
  }

  Future<Map<String, dynamic>> uploadFile(
    String path,
    String filePath, {
    String fieldName = 'file',
    void Function(int sent, int total)? onProgress,
  }) async {
    try {
      final multipartFile = await MultipartFile.fromFile(filePath);
      final formData = FormData.fromMap({fieldName: multipartFile});
      final response = await _dio.post(
        path,
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
        onSendProgress: onProgress,
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw mapDioException(e);
    }
  }

  bool _isRetryableTimeout(DioException e) {
    final isGet = e.requestOptions.method == 'GET';
    final isTimeout = e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.receiveTimeout;
    return isGet && isTimeout;
  }
}

final apiServiceProvider = Provider<ApiService>((ref) {
  throw UnimplementedError('apiServiceProvider must be overridden in main()');
});

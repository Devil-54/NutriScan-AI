import 'package:dio/dio.dart';

import 'api_exception.dart';

ApiException mapDioException(DioException e) {
  switch (e.type) {
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.sendTimeout:
    case DioExceptionType.receiveTimeout:
    case DioExceptionType.transformTimeout:
      return const TimeoutApiException();
    case DioExceptionType.connectionError:
      return const NoInternetException();
    case DioExceptionType.badResponse:
      return _mapStatusCode(e.response);
    case DioExceptionType.cancel:
      return const UnknownApiException('Request was cancelled.');
    case DioExceptionType.badCertificate:
    case DioExceptionType.unknown:
      return const UnknownApiException();
  }
}

ApiException _mapStatusCode(Response? response) {
  final status = response?.statusCode ?? 0;
  final data = response?.data;
  final error = (data is Map && data['error'] is Map) ? data['error'] as Map : null;
  final message = error?['message'] as String?;
  final code = error?['code'] as String?;

  switch (status) {
    case 400:
    case 422:
      return ValidationApiException(message ?? 'Please check your input and try again.', code: code);
    case 401:
      return UnauthorizedException(message, code);
    case 403:
      return ForbiddenException(message, code);
    case 404:
      return NotFoundException(message, code);
    case 409:
      return ConflictException(message, code);
    case 429:
      return ValidationApiException(message ?? 'Too many requests - please try again shortly.', code: code);
    case >= 500:
      return ServerException(message);
    default:
      return UnknownApiException(message);
  }
}

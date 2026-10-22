/// Typed exceptions for API failures - UI layers catch these and show
/// user-friendly messages instead of raw DioExceptions. Mirrors the
/// backend's {success:false, error:{code,message}} envelope plus
/// transport-level failures (timeout, no internet).
sealed class ApiException implements Exception {
  const ApiException(this.message, {this.code});
  final String message;
  final String? code;
}

class NoInternetException extends ApiException {
  const NoInternetException() : super('No internet connection. Please check your network.');
}

class TimeoutApiException extends ApiException {
  const TimeoutApiException() : super('The request took too long. Please try again.');
}

class UnauthorizedException extends ApiException {
  const UnauthorizedException([String? message, String? code])
      : super(message ?? 'Your session has expired. Please log in again.', code: code);
}

class ForbiddenException extends ApiException {
  const ForbiddenException([String? message, String? code])
      : super(message ?? "You don't have permission to do that.", code: code);
}

class NotFoundException extends ApiException {
  const NotFoundException([String? message, String? code])
      : super(message ?? 'The requested item could not be found.', code: code);
}

class ValidationApiException extends ApiException {
  const ValidationApiException(super.message, {super.code});
}

class ConflictException extends ApiException {
  const ConflictException([String? message, String? code])
      : super(message ?? 'This already exists.', code: code);
}

class ServerException extends ApiException {
  const ServerException([String? message]) : super(message ?? 'Something went wrong on our end. Please try again.');
}

class UnknownApiException extends ApiException {
  const UnknownApiException([String? message]) : super(message ?? 'An unexpected error occurred.');
}

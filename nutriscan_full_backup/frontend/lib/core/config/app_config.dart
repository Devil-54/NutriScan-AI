/// App-wide runtime configuration. Values here are compile-time defaults;
/// override at build time with --dart-define for staging/prod builds, e.g.:
///   flutter run --dart-define=API_BASE_URL=https://api.nutriscan.app/api/v1
class AppConfig {
  AppConfig._();

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  static const bool isProduction = bool.fromEnvironment(
    'IS_PRODUCTION',
    defaultValue: false,
  );

  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 30);
}

enum Environment { development, staging, production }

class EnvConfig {
  EnvConfig._();

  static const Environment current = Environment.development;

  static bool get isDevelopment => current == Environment.development;
  static bool get isProduction => current == Environment.production;
}

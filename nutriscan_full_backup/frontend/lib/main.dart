import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/constants/app_constants.dart';
import 'core/router/app_router.dart';
import 'core/services/api_service.dart';
import 'core/services/secure_storage_service.dart';
import 'core/services/storage_service.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/theme_provider.dart';
import 'features/authentication/presentation/providers/auth_provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final storageService = StorageService(prefs);
  final secureStorage = SecureStorageService();

  // One-time migration: JWTs used to live in SharedPreferences (pre-secure-storage).
  // Move any existing tokens into secure storage so existing sessions survive the
  // upgrade instead of silently logging users out.
  await _migrateLegacyTokens(storageService, secureStorage);

  runApp(
    ProviderScope(
      overrides: [
        storageServiceProvider.overrideWithValue(storageService),
        secureStorageServiceProvider.overrideWithValue(secureStorage),
        apiServiceProvider.overrideWith((ref) {
          return ApiService(
            storage: ref.watch(secureStorageServiceProvider),
            onSessionExpired: () => ref.read(authProvider.notifier).forceLogout(),
          );
        }),
      ],
      child: const NutriScanApp(),
    ),
  );
}

Future<void> _migrateLegacyTokens(StorageService legacy, SecureStorageService secure) async {
  final legacyAccess = legacy.getString(AppConstants.keyAccessToken);
  final legacyRefresh = legacy.getString(AppConstants.keyRefreshToken);

  if (legacyAccess != null) {
    await secure.setString(AppConstants.keyAccessToken, legacyAccess);
    await legacy.remove(AppConstants.keyAccessToken);
  }
  if (legacyRefresh != null) {
    await secure.setString(AppConstants.keyRefreshToken, legacyRefresh);
    await legacy.remove(AppConstants.keyRefreshToken);
  }
}

class NutriScanApp extends ConsumerWidget {
  const NutriScanApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp.router(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeMode,
      routerConfig: router,
    );
  }
}

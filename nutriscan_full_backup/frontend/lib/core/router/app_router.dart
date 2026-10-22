import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/authentication/presentation/providers/auth_provider.dart';
import '../../features/authentication/presentation/screens/forgot_password_screen.dart';
import '../../features/authentication/presentation/screens/login_screen.dart';
import '../../features/authentication/presentation/screens/onboarding_screen.dart';
import '../../features/authentication/presentation/screens/register_screen.dart';
import '../../features/authentication/presentation/screens/splash_screen.dart';
import '../../features/history/presentation/screens/history_screen.dart';
import '../../features/history/presentation/screens/scan_details_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/profile/presentation/screens/health_profile_screen.dart';
import '../../features/profile/presentation/screens/profile_screen.dart';
import '../../features/recipes/domain/recipe_data.dart';
import '../../features/recipes/presentation/screens/recipe_details_screen.dart';
import '../../features/recipes/presentation/screens/recipes_screen.dart';
import '../../features/reminders/presentation/screens/reminder_center_screen.dart';
import '../../features/result/data/recommendation_model.dart';
import '../../features/result/data/scan_analysis_payload.dart';
import '../../features/result/presentation/screens/ai_analysis_screen.dart';
import '../../features/result/presentation/screens/result_screen.dart';
import '../../features/scan/presentation/screens/camera_preview_screen.dart';
import '../../features/scan/presentation/screens/gallery_picker_screen.dart';
import '../../features/scan/presentation/screens/image_preview_screen.dart';
import '../../features/scan/presentation/screens/scan_screen.dart';
import '../../features/scan/presentation/screens/scanning_screen.dart';
import '../../features/settings/presentation/screens/about_screen.dart';
import '../../features/settings/presentation/screens/settings_screen.dart';
import '../constants/route_constants.dart';
import 'main_shell.dart';

/// Central router provider. Watches [authProvider] so the router rebuilds
/// (and re-evaluates [redirect]) whenever login/logout/session-expiry
/// changes auth state - this is what makes onSessionExpired (see
/// api_service.dart + main.dart) actually bounce the user to Login.
///
/// Home/Scan/History/Profile/Recipes live inside a StatefulShellRoute so the
/// bottom NavigationBar (see main_shell.dart) persists across tab switches
/// and each tab keeps its own navigation stack. Result and the camera/gallery/
/// preview/scanning screens are reached by pushing from the Scan tab but are
/// full-screen, bottom-nav-free experiences, so they stay plain top-level routes.
final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  const publicRoutes = {
    RouteConstants.splash,
    RouteConstants.onboarding,
    RouteConstants.login,
    RouteConstants.register,
    RouteConstants.forgotPassword,
  };

  return GoRouter(
    initialLocation: RouteConstants.splash,
    debugLogDiagnostics: true,
    redirect: (context, state) {
      // Splash owns the initial routing decision (it awaits authProvider
      // itself before navigating) - never redirect away from it, and never
      // redirect while auth state is still loading to avoid flicker.
      if (state.matchedLocation == RouteConstants.splash || authState.isLoading) {
        return null;
      }

      final isLoggedIn = authState.valueOrNull != null;
      final isPublicRoute = publicRoutes.contains(state.matchedLocation);

      if (!isLoggedIn && !isPublicRoute) return RouteConstants.login;
      if (isLoggedIn &&
          (state.matchedLocation == RouteConstants.login ||
              state.matchedLocation == RouteConstants.register)) {
        return RouteConstants.home;
      }
      return null;
    },
    routes: [
      GoRoute(
        path: RouteConstants.splash,
        name: RouteConstants.splashName,
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: RouteConstants.onboarding,
        name: RouteConstants.onboardingName,
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: RouteConstants.login,
        name: RouteConstants.loginName,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: RouteConstants.register,
        name: RouteConstants.registerName,
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: RouteConstants.forgotPassword,
        name: RouteConstants.forgotPasswordName,
        builder: (context, state) => const ForgotPasswordScreen(),
      ),
      GoRoute(
        path: RouteConstants.result,
        name: RouteConstants.resultName,
        builder: (context, state) => ResultScreen(
          key: UniqueKey(),
          result:
              state.extra is (RecommendationResultModel, ScanAnalysisPayload?)
                  ? (state.extra as (
                      RecommendationResultModel,
                      ScanAnalysisPayload?
                    ))
                      .$1
                  : state.extra as RecommendationResultModel?,
          payload:
              state.extra is (RecommendationResultModel, ScanAnalysisPayload?)
                  ? (state.extra as (
                      RecommendationResultModel,
                      ScanAnalysisPayload?
                    ))
                      .$2
                  : null,
        ),
      ),
      GoRoute(
        path: RouteConstants.cameraPreview,
        name: RouteConstants.cameraPreviewName,
        builder: (context, state) => const CameraPreviewScreen(),
      ),
      GoRoute(
        path: RouteConstants.galleryPicker,
        name: RouteConstants.galleryPickerName,
        builder: (context, state) => const GalleryPickerScreen(),
      ),
      GoRoute(
        path: RouteConstants.imagePreview,
        name: RouteConstants.imagePreviewName,
        builder: (context, state) => ImagePreviewScreen(
          key: UniqueKey(),
          imagePath: state.extra as String?,
        ),
      ),
      GoRoute(
        path: RouteConstants.scanningProgress,
        name: RouteConstants.scanningProgressName,
        builder: (context, state) => ScanningScreen(
          key: UniqueKey(),
          imagePath: state.extra as String?,
        ),
      ),
      GoRoute(
        path: RouteConstants.aiAnalysis,
        name: RouteConstants.aiAnalysisName,
        builder: (context, state) => AiAnalysisScreen(
          key: UniqueKey(),
          payload: state.extra is ScanAnalysisPayload
              ? state.extra as ScanAnalysisPayload
              : ScanAnalysisPayload(
                  scanId: '',
                  ocrText: state.extra as String? ?? '',
                  scanTime: DateTime.now()),
        ),
      ),
      GoRoute(
        path: RouteConstants.healthProfile,
        name: RouteConstants.healthProfileName,
        builder: (context, state) => const HealthProfileScreen(),
      ),
      GoRoute(
        path: RouteConstants.scanDetails,
        name: RouteConstants.scanDetailsName,
        builder: (context, state) => ScanDetailsScreen(
          key: ValueKey(state.extra as String?),
          scanId: state.extra as String?,
        ),
      ),
      GoRoute(
        path: RouteConstants.about,
        name: RouteConstants.aboutName,
        builder: (context, state) => const AboutScreen(),
      ),
      GoRoute(
        path: RouteConstants.settings,
        name: RouteConstants.settingsName,
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: RouteConstants.reminders,
        name: RouteConstants.remindersName,
        builder: (context, state) => const ReminderCenterScreen(),
      ),
      GoRoute(
        path: RouteConstants.recipeDetails,
        name: RouteConstants.recipeDetailsName,
        builder: (context, state) =>
            RecipeDetailsScreen(recipe: state.extra as Recipe),
      ),
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) =>
            MainShell(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteConstants.home,
                name: RouteConstants.homeName,
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteConstants.scan,
                name: RouteConstants.scanName,
                builder: (context, state) => const ScanScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteConstants.history,
                name: RouteConstants.historyName,
                builder: (context, state) => const HistoryScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteConstants.profile,
                name: RouteConstants.profileName,
                builder: (context, state) => const ProfileScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteConstants.recipes,
                name: RouteConstants.recipesName,
                builder: (context, state) => const RecipesScreen(),
              ),
            ],
          ),
        ],
      ),
    ],
  );
});

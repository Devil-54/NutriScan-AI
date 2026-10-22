import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/services/api_service.dart';
import '../../../../core/services/secure_storage_service.dart';
import '../../data/auth_remote_datasource.dart';
import '../../data/auth_repository.dart';
import '../../data/user_model.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final api = ref.watch(apiServiceProvider);
  final storage = ref.watch(secureStorageServiceProvider);
  return AuthRepository(AuthRemoteDatasource(api), storage);
});

/// Null = logged out. Login/register don't set this directly - callers
/// should call `ref.read(authProvider.notifier).loadCurrentUser()` after a
/// successful login, or check `await authRepositoryProvider.isLoggedIn` for a
/// cheap token-presence check (e.g. in the splash screen).
class AuthNotifier extends AsyncNotifier<UserModel?> {
  @override
  Future<UserModel?> build() async {
    if (!await ref.read(authRepositoryProvider).isLoggedIn) return null;
    try {
      return await ref.read(authRepositoryProvider).getCurrentUser();
    } catch (_) {
      return null;
    }
  }

  Future<void> login({required String email, required String password}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await ref.read(authRepositoryProvider).login(email: email, password: password);
      return ref.read(authRepositoryProvider).getCurrentUser();
    });
  }

  Future<void> register({required String name, required String email, required String password}) async {
    await ref.read(authRepositoryProvider).register(name: name, email: email, password: password);
  }

  Future<void> forgotPassword(String email) => ref.read(authRepositoryProvider).forgotPassword(email);

  Future<void> logout() async {
    await ref.read(authRepositoryProvider).logout();
    state = const AsyncData(null);
  }

  /// Called by ApiService's onSessionExpired (refresh-token failure) - the
  /// interceptor already cleared stored tokens, this just updates app state
  /// so the router's redirect bounces to Login.
  void forceLogout() {
    state = const AsyncData(null);
  }
}

final authProvider = AsyncNotifierProvider<AuthNotifier, UserModel?>(AuthNotifier.new);

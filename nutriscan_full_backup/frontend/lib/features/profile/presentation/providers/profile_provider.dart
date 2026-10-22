import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/services/api_service.dart';
import '../../data/profile_model.dart';
import '../../data/profile_remote_datasource.dart';
import '../../data/profile_repository.dart';

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepository(ProfileRemoteDatasource(ref.watch(apiServiceProvider)));
});

final healthProfileProvider = AsyncNotifierProvider<HealthProfileNotifier, HealthProfileModel?>(
  HealthProfileNotifier.new,
);

class HealthProfileNotifier extends AsyncNotifier<HealthProfileModel?> {
  @override
  Future<HealthProfileModel?> build() async {
    final full = await ref.read(profileRepositoryProvider).getProfile();
    return full.healthProfile;
  }

  Future<void> save(HealthProfileModel profile) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => ref.read(profileRepositoryProvider).updateProfile(profile));
  }
}

class ProfileStats {
  const ProfileStats({required this.totalScans, required this.safeFoods, required this.warnings});
  final int totalScans;
  final int safeFoods;
  final int warnings;
}

final profileStatsProvider = FutureProvider<ProfileStats>((ref) async {
  final response = await ref.watch(apiServiceProvider).get('/scans/history/stats');
  final data = Map<String, dynamic>.from(response['data'] as Map);
  return ProfileStats(
    totalScans: data['total_scans'] as int? ?? 0,
    safeFoods: data['safe_foods'] as int? ?? 0,
    warnings: data['warnings'] as int? ?? 0,
  );
});

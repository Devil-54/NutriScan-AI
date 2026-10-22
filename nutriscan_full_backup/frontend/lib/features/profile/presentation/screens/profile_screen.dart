import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/animation_utils.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../../../shared/widgets/loading_indicator.dart';
import '../../../../shared/widgets/section_header.dart';
import '../../../../shared/widgets/statistic_card.dart';
import '../../../authentication/presentation/providers/auth_provider.dart';
import '../../domain/profile_dummy_data.dart';
import '../providers/profile_provider.dart';
import '../widgets/profile_header.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);
    final user = ref.watch(authProvider).valueOrNull;
    final statsAsync = ref.watch(profileStatsProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Profile', showBackButton: false),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
              children: [
                AppAnimations.fadeSlideUp(
                  ProfileHeader(
                    name: user?.name ?? dummyUserName,
                    email: user?.email ?? dummyUserEmail,
                    membershipStatus: dummyMembershipStatus,
                    onEditPressed: () => context.goNamed(RouteConstants.healthProfileName),
                  ),
                ),
                const SizedBox(height: 24),
                statsAsync.when(
                  data: (stats) => Row(
                    children: [
                      Expanded(child: StatisticCard(value: '${stats.totalScans}', label: 'Total Scans')),
                      const SizedBox(width: 10),
                      Expanded(
                        child: StatisticCard(value: '${stats.safeFoods}', label: 'Safe Foods', color: AppColors.success),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: StatisticCard(value: '${stats.warnings}', label: 'Warnings', color: AppColors.warning),
                      ),
                    ],
                  ),
                  loading: () => const SizedBox(height: 88, child: Center(child: LoadingIndicator())),
                  error: (_, __) => const Row(
                    children: [
                      Expanded(child: StatisticCard(value: '—', label: 'Total Scans')),
                      SizedBox(width: 10),
                      Expanded(child: StatisticCard(value: '—', label: 'Safe Foods', color: AppColors.success)),
                      SizedBox(width: 10),
                      Expanded(child: StatisticCard(value: '—', label: 'Warnings', color: AppColors.warning)),
                    ],
                  ),
                ),
                const SizedBox(height: 28),
                SectionHeader(
                  title: 'Health Profile',
                  actionLabel: 'Edit',
                  onActionTap: () => context.goNamed(RouteConstants.healthProfileName),
                ),
                const SizedBox(height: 12),
                CustomCard(
                  onTap: () => context.goNamed(RouteConstants.healthProfileName),
                  child: Row(
                    children: [
                      const Icon(Icons.favorite_rounded, color: AppColors.primary),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Age, weight, medical conditions, allergies, fitness goals',
                          style: AppTextStyles.subtext(),
                        ),
                      ),
                      const Icon(Icons.chevron_right_rounded, color: AppColors.subtext),
                    ],
                  ),
                ),
                const SizedBox(height: 28),
                const SectionHeader(title: 'Achievements'),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    for (final achievement in dummyAchievements)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        decoration: BoxDecoration(
                          color: AppColors.secondary.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.emoji_events_rounded, color: AppColors.secondary, size: 16),
                            const SizedBox(width: 6),
                            Text(achievement, style: AppTextStyles.bodyMedium(color: AppColors.secondary)),
                          ],
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

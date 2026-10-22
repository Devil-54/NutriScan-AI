import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/animation_utils.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/loading_indicator.dart';
import '../../../../shared/widgets/section_header.dart';
import '../../../history/presentation/providers/history_provider.dart';
import '../../domain/dashboard_dummy_data.dart';
import '../widgets/daily_tip_card.dart';
import '../widgets/greeting_header.dart';
import '../widgets/health_summary_card.dart';
import '../widgets/quick_actions_grid.dart';
import '../widgets/quick_scan_button.dart';
import '../widgets/recent_scan_card.dart';
import '../widgets/recommendation_card.dart';
import '../../../authentication/presentation/providers/auth_provider.dart';

/// Greeting name and Recent Scans reuse existing auth/history providers
/// (real API data). Health Summary stats, Daily Tip, and "Recommended for
/// You" have no matching backend endpoint (no aggregate daily-stats or
/// generic recommendation-feed API exists) so they remain illustrative
/// dummy content per Phase 4G scope - not a bug, a genuine API gap.
String _firstUnsafeFoodOrDefault(Map<String, dynamic> item) {
  final unsafe = (item['unsafe_foods'] as List?)?.cast<String>();
  return (unsafe != null && unsafe.isNotEmpty) ? unsafe.first : 'Food Scan';
}

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  static final _healthTip = dummyHealthTips[0];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);
    final userAsync = ref.watch(authProvider);
    final historyAsync = ref.watch(scanHistoryProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
              children: [
                GreetingHeader(userName: userAsync.valueOrNull?.name ?? 'there'),
                const SizedBox(height: 24),
                AppAnimations.fadeSlideUp(
                  const HealthSummaryCard(healthScore: 78, todaysScans: 3, safeFoods: 2, warnings: 1),
                ),
                const SizedBox(height: 28),
                AppAnimations.fadeIn(const QuickScanButton(), delay: const Duration(milliseconds: 100)),
                const SizedBox(height: 28),
                AppAnimations.fadeIn(DailyTipCard(tip: _healthTip), delay: const Duration(milliseconds: 150)),
                const SizedBox(height: 28),
                const SectionHeader(title: 'Recent Scans'),
                const SizedBox(height: 12),
                historyAsync.when(
                  loading: () => const Padding(padding: EdgeInsets.all(16), child: LoadingIndicator(size: 24)),
                  error: (error, _) => Text('Could not load recent scans.', style: AppTextStyles.subtext()),
                  data: (items) {
                    if (items.isEmpty) {
                      return Text('No scans yet - tap Scan Food to get started.', style: AppTextStyles.subtext());
                    }
                    final recent = items.take(3).toList();
                    return Column(
                      children: [
                        for (int i = 0; i < recent.length; i++) ...[
                          AppAnimations.staggeredItem(
                            RecentScanCard(
                              item: RecentScanItem(
                                name: _firstUnsafeFoodOrDefault(recent[i]),
                                healthScore: (recent[i]['recommendation_score'] as num?)?.round() ?? 0,
                                riskLabel: switch (recent[i]['status'] as String?) {
                                  'safe' => 'Safe',
                                  'unsafe' => 'Unsafe',
                                  _ => 'Moderate Risk',
                                },
                                dateLabel: (recent[i]['created_at'] as String?)?.split('T').first ?? '',
                              ),
                            ),
                            i,
                          ),
                          if (i != recent.length - 1) const SizedBox(height: 10),
                        ],
                      ],
                    );
                  },
                ),
                const SizedBox(height: 28),
                const SectionHeader(title: 'Recommended for You'),
                const SizedBox(height: 12),
                AppAnimations.fadeIn(const RecommendationCard(items: dummyRecommendations)),
                const SizedBox(height: 28),
                const SectionHeader(title: 'Quick Actions'),
                const SizedBox(height: 12),
                const QuickActionsGrid(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

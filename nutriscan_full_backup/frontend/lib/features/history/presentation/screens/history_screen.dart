import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/utils/animation_utils.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/empty_state_widget.dart';
import '../../../../shared/widgets/loading_indicator.dart';
import '../../domain/history_dummy_data.dart';
import '../providers/history_provider.dart';
import '../widgets/history_card.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Scan History', showBackButton: false),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ref.watch(scanHistoryProvider).when(
              loading: () => const Center(child: LoadingIndicator()),
              error: (_, __) => Center(
                child: TextButton(
                  onPressed: () => ref.invalidate(scanHistoryProvider),
                  child: const Text('Could not load your scan history. Retry'),
                ),
              ),
              data: (items) {
                final entries = items.map(ScanHistoryEntry.fromApi).toList();
                if (entries.isEmpty) {
                  return const EmptyStateWidget(
                    icon: Icons.history,
                    title: 'No completed scans yet',
                    message: 'Your personalized scan results will appear here.',
                  );
                }
                return RefreshIndicator(
                  onRefresh: () async => ref.refresh(scanHistoryProvider.future),
                  child: ListView.separated(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
                    itemCount: entries.length,
                    separatorBuilder: (context, index) => const SizedBox(height: 10),
                    itemBuilder: (context, i) => AppAnimations.staggeredItem(
                      HistoryCard(
                        entry: entries[i],
                        onQuickView: () => context.goNamed(RouteConstants.scanDetailsName, extra: entries[i].scanId),
                      ),
                      i,
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}

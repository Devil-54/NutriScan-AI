import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_card.dart';

class _QuickAction {
  const _QuickAction({required this.label, required this.icon, required this.onTap});
  final String label;
  final IconData icon;
  final VoidCallback onTap;
}

class QuickActionsGrid extends StatelessWidget {
  const QuickActionsGrid({super.key});

  @override
  Widget build(BuildContext context) {
    final actions = [
      _QuickAction(
        label: 'History',
        icon: Icons.history_rounded,
        onTap: () => context.goNamed(RouteConstants.historyName),
      ),
      _QuickAction(
        label: 'Profile',
        icon: Icons.person_outline_rounded,
        onTap: () => context.goNamed(RouteConstants.profileName),
      ),
      _QuickAction(label: 'Health Goals', icon: Icons.flag_outlined, onTap: () {}),
      _QuickAction(label: 'Saved Foods', icon: Icons.bookmark_outline_rounded, onTap: () {}),
    ];

    final columns = ResponsiveUtils.value(context, mobile: 2, tablet: 4, desktop: 4);

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: actions.length,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: columns,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.3,
      ),
      itemBuilder: (context, index) {
        final action = actions[index];
        return CustomCard(
          onTap: action.onTap,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(action.icon, color: AppColors.primary, size: 26),
              const SizedBox(height: 8),
              Text(action.label, style: AppTextStyles.caption(color: AppColors.text), textAlign: TextAlign.center),
            ],
          ),
        );
      },
    );
  }
}

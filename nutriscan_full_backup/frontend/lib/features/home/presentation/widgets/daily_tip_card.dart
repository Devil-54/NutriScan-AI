import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';

class DailyTipCard extends StatelessWidget {
  const DailyTipCard({super.key, required this.tip});

  final String tip;

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      color: AppColors.secondary.withValues(alpha: 0.08),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(color: AppColors.secondary.withValues(alpha: 0.15), shape: BoxShape.circle),
            child: const Icon(Icons.lightbulb_outline_rounded, color: AppColors.secondary),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("Today's Health Tip", style: AppTextStyles.caption()),
                const SizedBox(height: 2),
                Text(tip, style: AppTextStyles.bodyMedium()),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

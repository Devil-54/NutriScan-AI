import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../domain/dashboard_dummy_data.dart';

class RecentScanCard extends StatelessWidget {
  const RecentScanCard({super.key, required this.item});

  final RecentScanItem item;

  Color get _riskColor {
    if (item.healthScore >= 75) return AppColors.success;
    if (item.healthScore >= 50) return AppColors.warning;
    return AppColors.error;
  }

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      padding: const EdgeInsets.all(14),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: _riskColor.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(Icons.fastfood_rounded, color: _riskColor, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.name, style: AppTextStyles.bodyMedium(), maxLines: 1, overflow: TextOverflow.ellipsis),
                const SizedBox(height: 4),
                Text(item.dateLabel, style: AppTextStyles.caption()),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('${item.healthScore}', style: AppTextStyles.title(color: _riskColor)),
              Text(item.riskLabel, style: AppTextStyles.caption(color: _riskColor)),
            ],
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../domain/result_dummy_data.dart';

class RiskBadge extends StatelessWidget {
  const RiskBadge({super.key, required this.riskLevel});

  final RiskLevel riskLevel;

  Color get _color => switch (riskLevel) {
        RiskLevel.safe => AppColors.success,
        RiskLevel.lowRisk => AppColors.success,
        RiskLevel.moderateRisk => AppColors.warning,
        RiskLevel.highRisk => AppColors.error,
        RiskLevel.unsafe => AppColors.error,
      };

  IconData get _icon => switch (riskLevel) {
        RiskLevel.safe || RiskLevel.lowRisk => Icons.check_circle_rounded,
        RiskLevel.moderateRisk => Icons.warning_rounded,
        RiskLevel.highRisk || RiskLevel.unsafe => Icons.dangerous_rounded,
      };

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(color: _color.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(20)),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_icon, color: _color, size: 16),
          const SizedBox(width: 6),
          Text(riskLevel.label, style: AppTextStyles.bodyMedium(color: _color)),
        ],
      ),
    );
  }
}

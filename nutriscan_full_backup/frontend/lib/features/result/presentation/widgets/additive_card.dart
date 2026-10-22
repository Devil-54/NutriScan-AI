import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../domain/result_dummy_data.dart';

class AdditiveCard extends StatelessWidget {
  const AdditiveCard({super.key, required this.additive});

  final AdditiveResult additive;

  Color get _riskColor => switch (additive.riskLevel.toLowerCase()) {
        'low' => AppColors.success,
        'moderate' => AppColors.warning,
        _ => AppColors.error,
      };

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(additive.insNumber, style: AppTextStyles.caption(color: AppColors.primary)),
              ),
              const SizedBox(width: 8),
              Expanded(child: Text(additive.purpose, style: AppTextStyles.bodyMedium())),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: _riskColor.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(12)),
                child: Text(additive.riskLevel, style: AppTextStyles.caption(color: _riskColor)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(additive.explanation, style: AppTextStyles.subtext()),
        ],
      ),
    );
  }
}

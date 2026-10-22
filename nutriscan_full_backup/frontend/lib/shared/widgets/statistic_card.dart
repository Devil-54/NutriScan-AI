import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import 'custom_card.dart';

class StatisticCard extends StatelessWidget {
  const StatisticCard({super.key, required this.value, required this.label, this.color = AppColors.primary});

  final String value;
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
      child: Column(
        children: [
          Text(value, style: AppTextStyles.displaySmall(color: color)),
          const SizedBox(height: 4),
          Text(label, style: AppTextStyles.caption(), textAlign: TextAlign.center),
        ],
      ),
    );
  }
}

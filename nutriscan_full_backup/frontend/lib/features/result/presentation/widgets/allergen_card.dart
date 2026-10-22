import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';

class AllergenCard extends StatelessWidget {
  const AllergenCard({super.key, required this.name, required this.isDetected});

  final String name;
  final bool isDetected;

  @override
  Widget build(BuildContext context) {
    final color = isDetected ? AppColors.error : AppColors.subtext;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: isDetected ? AppColors.error.withValues(alpha: 0.1) : AppColors.card,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: isDetected ? AppColors.error.withValues(alpha: 0.3) : Colors.grey.shade200),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isDetected ? Icons.warning_rounded : Icons.check_circle_outline_rounded,
            color: color,
            size: 16,
          ),
          const SizedBox(width: 6),
          Text(name, style: AppTextStyles.bodyMedium(color: isDetected ? AppColors.error : AppColors.text)),
        ],
      ),
    );
  }
}

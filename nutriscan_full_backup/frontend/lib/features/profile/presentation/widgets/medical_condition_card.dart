import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';

class MedicalConditionCard extends StatelessWidget {
  const MedicalConditionCard({super.key, required this.label, required this.icon, required this.selected, required this.onTap});

  final String label;
  final String icon;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
        decoration: BoxDecoration(
          color: selected ? AppColors.primary.withValues(alpha: 0.1) : AppColors.card,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: selected ? AppColors.primary : Colors.grey.shade200, width: selected ? 1.5 : 1),
        ),
        child: Column(
          children: [
            Text(icon, style: const TextStyle(fontSize: 24)),
            const SizedBox(height: 8),
            Text(
              label,
              style: AppTextStyles.caption(color: selected ? AppColors.primary : AppColors.text),
              textAlign: TextAlign.center,
            ),
            if (selected) ...[
              const SizedBox(height: 4),
              const Icon(Icons.check_circle_rounded, color: AppColors.primary, size: 14),
            ],
          ],
        ),
      ),
    );
  }
}

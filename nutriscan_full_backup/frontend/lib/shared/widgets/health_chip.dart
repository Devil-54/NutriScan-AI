import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';

/// Selectable pill chip used across Health Profile (gender, diet preference,
/// fitness goal, activity level, etc). Visual selection state only - no
/// persistence/business logic (Phase 4F scope).
class HealthChip extends StatelessWidget {
  const HealthChip({super.key, required this.label, required this.selected, required this.onTap, this.icon});

  final String label;
  final bool selected;
  final VoidCallback? onTap;
  final String? icon;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: selected ? AppColors.primary : Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: selected ? AppColors.primary : Colors.grey.shade300),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[Text(icon!, style: const TextStyle(fontSize: 14)), const SizedBox(width: 6)],
            Text(label, style: AppTextStyles.bodyMedium(color: selected ? Colors.white : Theme.of(context).colorScheme.onSurface)),
          ],
        ),
      ),
    );
  }
}

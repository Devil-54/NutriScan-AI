import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';

/// Displays one editable health-profile field. Tapping shows an edit
/// affordance only - no persistence/business logic (Phase 4F scope).
class EditableProfileCard extends StatelessWidget {
  const EditableProfileCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    this.onTap,
  });

  final String label;
  final String value;
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      onTap: onTap,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(12)),
            child: Icon(icon, color: AppColors.primary, size: 20),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: AppTextStyles.caption()),
                const SizedBox(height: 2),
                Text(value, style: AppTextStyles.bodyMedium()),
              ],
            ),
          ),
          const Icon(Icons.edit_outlined, color: AppColors.subtext, size: 18),
        ],
      ),
    );
  }
}

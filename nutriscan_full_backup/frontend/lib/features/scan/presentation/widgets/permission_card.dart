import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';

class PermissionCard extends StatelessWidget {
  const PermissionCard({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
  });

  final IconData icon;
  final String title;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 140,
          height: 140,
          decoration: BoxDecoration(
            gradient: RadialGradient(
              colors: [AppColors.primary.withValues(alpha: 0.14), AppColors.primary.withValues(alpha: 0.02)],
            ),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, size: 62, color: AppColors.primary),
        ).animate().fadeIn(duration: 400.ms).scale(begin: const Offset(0.85, 0.85), curve: Curves.easeOutBack),
        const SizedBox(height: 28),
        Text(title, style: AppTextStyles.displaySmall(), textAlign: TextAlign.center)
            .animate()
            .fadeIn(duration: 350.ms, delay: 100.ms),
        const SizedBox(height: 10),
        Text(message, style: AppTextStyles.body(color: AppColors.subtext), textAlign: TextAlign.center)
            .animate()
            .fadeIn(duration: 350.ms, delay: 160.ms),
      ],
    );
  }
}

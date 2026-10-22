import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';

class AuthHeader extends StatelessWidget {
  const AuthHeader(
      {super.key,
      required this.title,
      required this.subtitle,
      this.showLogo = true});

  final String title;
  final String subtitle;
  final bool showLogo;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        if (showLogo) ...[
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppColors.primary, AppColors.secondary],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                    color: AppColors.primary.withValues(alpha: 0.22),
                    blurRadius: 16,
                    offset: const Offset(0, 8))
              ],
            ),
            child: const Icon(Icons.health_and_safety_rounded,
                color: Colors.white, size: 32),
          )
              .animate()
              .fadeIn(duration: 300.ms)
              .scale(begin: const Offset(0.9, 0.9)),
          const SizedBox(height: 14),
          Text('NutriScan',
              style: AppTextStyles.headline(color: AppColors.primary)),
          const SizedBox(height: 2),
          Text('AI Powered Food Safety Analysis',
              style: AppTextStyles.caption()),
          const SizedBox(height: 26),
        ],
        Text(title,
                style: AppTextStyles.displaySmall(),
                textAlign: TextAlign.center)
            .animate()
            .fadeIn(duration: 350.ms),
        const SizedBox(height: 8),
        Text(subtitle,
                style: AppTextStyles.subtext(), textAlign: TextAlign.center)
            .animate()
            .fadeIn(duration: 350.ms, delay: 80.ms),
      ],
    );
  }
}

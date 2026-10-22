import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../core/constants/app_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/secondary_button.dart';
import '../widgets/about_card.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'About NutriScan'),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
              children: [
                Center(
                  child: Column(
                    children: [
                      Container(
                        width: 84,
                        height: 84,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [AppColors.primary, AppColors.secondary],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(color: AppColors.primary.withValues(alpha: 0.25), blurRadius: 24, offset: const Offset(0, 12)),
                          ],
                        ),
                        child: const Icon(Icons.eco_rounded, color: Colors.white, size: 44),
                      ).animate().fadeIn(duration: 300.ms).scale(begin: const Offset(0.9, 0.9)),
                      const SizedBox(height: 16),
                      Text(AppConstants.appName, style: AppTextStyles.displaySmall()),
                      const SizedBox(height: 4),
                      Text('Version 0.1.0', style: AppTextStyles.subtext()),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                const AboutCard(
                  icon: Icons.info_outline_rounded,
                  title: 'About the Project',
                  description: 'NutriScan helps you understand packaged food instantly - scanning ingredient '
                      'labels, cross-checking allergens and additives, and giving personalized health guidance.',
                ).animate().fadeIn(duration: 300.ms, delay: 80.ms),
                const SizedBox(height: 12),
                const AboutCard(
                  icon: Icons.code_rounded,
                  title: 'Built With',
                  description: 'Flutter, Riverpod, go_router - powered by a FastAPI backend with OCR, a '
                      'Knowledge Graph, and a Medical Rule Engine.',
                ).animate().fadeIn(duration: 300.ms, delay: 130.ms),
                const SizedBox(height: 12),
                const AboutCard(
                  icon: Icons.person_outline_rounded,
                  title: 'Developer',
                  description: 'Built as an AI-powered personalized food safety project.',
                ).animate().fadeIn(duration: 300.ms, delay: 180.ms),
                const SizedBox(height: 24),
                SecondaryButton(label: 'View on GitHub', icon: Icons.open_in_new_rounded, onPressed: () {})
                    .animate()
                    .fadeIn(duration: 300.ms, delay: 220.ms),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';
import 'primary_button.dart';

class AppErrorWidget extends StatelessWidget {
  const AppErrorWidget({
    super.key,
    this.title = 'Something went wrong',
    this.message,
    this.onRetry,
    this.onBackToHome,
    this.onChooseAnotherImage,
  });

  final String title;
  final String? message;
  final VoidCallback? onRetry;
  final VoidCallback? onBackToHome;
  final VoidCallback? onChooseAnotherImage;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline_rounded, size: 56, color: AppColors.error),
            const SizedBox(height: 16),
            Text(title, style: AppTextStyles.title(), textAlign: TextAlign.center),
            if (message != null) ...[
              const SizedBox(height: 8),
              Text(message!, style: AppTextStyles.subtext(), textAlign: TextAlign.center),
            ],
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              PrimaryButton(label: 'Retry', onPressed: onRetry, isFullWidth: false, icon: Icons.refresh_rounded),
            ],
            if (onChooseAnotherImage != null) ...[
              const SizedBox(height: 12),
              OutlinedButton.icon(onPressed: onChooseAnotherImage, icon: const Icon(Icons.photo_library_outlined), label: const Text('Choose Another Image')),
            ],
            if (onBackToHome != null) ...[
              const SizedBox(height: 8),
              TextButton.icon(onPressed: onBackToHome, icon: const Icon(Icons.home_outlined), label: const Text('Back to Home')),
            ],
          ],
        ),
      ),
    );
  }
}

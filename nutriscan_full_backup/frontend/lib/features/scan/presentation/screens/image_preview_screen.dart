import 'dart:io';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../../../../shared/widgets/secondary_button.dart';

class ImagePreviewScreen extends StatelessWidget {
  const ImagePreviewScreen({super.key, this.imagePath});

  final String? imagePath;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Preview'),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: ResponsiveUtils.contentMaxWidth(context)),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: _buildImage(),
                    ),
                  ),
                  const SizedBox(height: 20),
                  PrimaryButton(
                    label: 'Start Scan',
                    icon: Icons.auto_awesome_rounded,
                    onPressed: imagePath != null && File(imagePath!).existsSync()
                        ? () => context.pushNamed(RouteConstants.scanningProgressName, extra: imagePath)
                        : null,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: SecondaryButton(
                          label: 'Retake',
                          icon: Icons.refresh_rounded,
                          onPressed: () => context.pop(),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: SecondaryButton(
                          label: 'Choose Another',
                          icon: Icons.photo_library_outlined,
                          onPressed: () => context.pushReplacementNamed(RouteConstants.galleryPickerName),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildImage() {
    if (imagePath != null && File(imagePath!).existsSync()) {
      return Image.file(File(imagePath!), fit: BoxFit.cover, width: double.infinity);
    }
    // No real file available (dummy gallery tile or camera unavailable) -
    // show a clearly-labeled placeholder rather than a broken image.
    return Container(
      color: AppColors.primary.withValues(alpha: 0.08),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.image_rounded, size: 64, color: AppColors.primary),
          const SizedBox(height: 12),
          Text('Sample preview image', style: AppTextStyles.subtext()),
        ],
      ),
    );
  }
}

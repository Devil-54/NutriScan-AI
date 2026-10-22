import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/animation_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/primary_button.dart';

class GalleryPickerScreen extends StatelessWidget {
  const GalleryPickerScreen({super.key});

  // Decorative placeholders only, per "dummy preview data" scope - tapping
  // one still proceeds with no real file (ImagePreviewScreen shows its own
  // placeholder state in that case).
  static const _dummyThumbnailColors = [
    AppColors.primary,
    AppColors.secondary,
    AppColors.warning,
    AppColors.success,
    AppColors.error,
    AppColors.primary,
  ];

  Future<void> _openSystemGallery(BuildContext context) async {
    try {
      final picked = await ImagePicker().pickImage(source: ImageSource.gallery);
      if (picked != null && context.mounted) {
        context.pushNamed(RouteConstants.imagePreviewName, extra: picked.path);
      }
    } catch (_) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Could not open the photo library. Please try again.')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Choose a Photo'),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            PrimaryButton(
              label: 'Browse Full Gallery',
              icon: Icons.photo_library_outlined,
              onPressed: () => _openSystemGallery(context),
            ),
            const SizedBox(height: 24),
            Text('Recent Photos', style: AppTextStyles.title()),
            const SizedBox(height: 12),
            Expanded(
              child: GridView.builder(
                itemCount: _dummyThumbnailColors.length,
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                ),
                itemBuilder: (context, index) {
                  final tile = ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Container(
                      color: _dummyThumbnailColors[index].withValues(alpha: 0.15),
                      child: Icon(Icons.image_rounded, color: _dummyThumbnailColors[index], size: 28),
                    ),
                  );
                  return InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () => _openSystemGallery(context),
                    child: AppAnimations.staggeredItem(tile, index),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

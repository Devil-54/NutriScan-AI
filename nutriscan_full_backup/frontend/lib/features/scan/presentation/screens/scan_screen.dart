import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../../../../shared/widgets/secondary_button.dart';
import '../widgets/permission_card.dart';

/// Entry point of the Scan bottom-nav tab: explains why camera access is
/// needed before jumping into the live camera preview. UI/navigation only -
/// the actual permission prompt happens natively when CameraPreviewScreen
/// initializes the `camera` plugin.
class ScanScreen extends StatelessWidget {
  const ScanScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Scan Food', showBackButton: false),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: ResponsiveUtils.contentMaxWidth(context)),
            child: Padding(
              padding: const EdgeInsets.all(28),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const PermissionCard(
                    icon: Icons.camera_alt_rounded,
                    title: 'Scan Your Food',
                    message:
                        'NutriScan needs camera access to read ingredient labels and give you instant, '
                        'personalized safety insights.',
                  ),
                  const SizedBox(height: 40),
                  PrimaryButton(
                    label: 'Allow Camera',
                    icon: Icons.camera_alt_rounded,
                    onPressed: () => context.pushNamed(RouteConstants.cameraPreviewName),
                  ),
                  const SizedBox(height: 12),
                  SecondaryButton(
                    label: 'Choose From Gallery',
                    icon: Icons.photo_library_outlined,
                    onPressed: () => context.pushNamed(RouteConstants.galleryPickerName),
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () => context.goNamed(RouteConstants.homeName),
                    child: const Text('Skip'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

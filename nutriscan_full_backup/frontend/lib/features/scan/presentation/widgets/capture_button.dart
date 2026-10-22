import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

class CaptureButton extends StatelessWidget {
  const CaptureButton({super.key, required this.onTap, this.isBusy = false});

  final VoidCallback onTap;
  final bool isBusy;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: isBusy ? null : onTap,
      child: Container(
        width: 76,
        height: 76,
        padding: const EdgeInsets.all(4),
        decoration: const BoxDecoration(shape: BoxShape.circle, color: Colors.white),
        child: Container(
          decoration: const BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(colors: [AppColors.primary, AppColors.secondary]),
          ),
          child: isBusy
              ? const Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white),
                )
              : null,
        ),
      ),
    );
  }
}

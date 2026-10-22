import 'package:flutter/material.dart';

import 'capture_button.dart';

class CameraBottomBar extends StatelessWidget {
  const CameraBottomBar({
    super.key,
    required this.onGalleryTap,
    required this.onCaptureTap,
    required this.onSwitchCameraTap,
    this.isCapturing = false,
  });

  final VoidCallback onGalleryTap;
  final VoidCallback onCaptureTap;
  final VoidCallback onSwitchCameraTap;
  final bool isCapturing;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _RoundButton(icon: Icons.photo_library_outlined, onTap: onGalleryTap),
        CaptureButton(onTap: onCaptureTap, isBusy: isCapturing),
        _RoundButton(icon: Icons.cameraswitch_outlined, onTap: onSwitchCameraTap),
      ],
    );
  }
}

class _RoundButton extends StatelessWidget {
  const _RoundButton({required this.icon, required this.onTap});

  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(26),
      child: Container(
        width: 52,
        height: 52,
        decoration: BoxDecoration(color: Colors.black.withValues(alpha: 0.35), shape: BoxShape.circle),
        child: Icon(icon, color: Colors.white, size: 24),
      ),
    );
  }
}

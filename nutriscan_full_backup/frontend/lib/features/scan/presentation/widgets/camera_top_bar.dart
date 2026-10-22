import 'package:flutter/material.dart';

class CameraTopBar extends StatelessWidget {
  const CameraTopBar({
    super.key,
    required this.isFlashOn,
    required this.onFlashToggle,
    required this.onClose,
    required this.onHelp,
  });

  final bool isFlashOn;
  final VoidCallback onFlashToggle;
  final VoidCallback onClose;
  final VoidCallback onHelp;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _CircleIconButton(icon: Icons.close_rounded, onTap: onClose),
        _CircleIconButton(
          icon: isFlashOn ? Icons.flash_on_rounded : Icons.flash_off_rounded,
          onTap: onFlashToggle,
        ),
        _CircleIconButton(icon: Icons.help_outline_rounded, onTap: onHelp),
      ],
    );
  }
}

class _CircleIconButton extends StatelessWidget {
  const _CircleIconButton({required this.icon, required this.onTap});

  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(color: Colors.black.withValues(alpha: 0.35), shape: BoxShape.circle),
        child: Icon(icon, color: Colors.white, size: 22),
      ),
    );
  }
}

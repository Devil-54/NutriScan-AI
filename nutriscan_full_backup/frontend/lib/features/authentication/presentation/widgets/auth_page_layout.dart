import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

class AuthPageLayout extends StatelessWidget {
  const AuthPageLayout({super.key, required this.child, this.maxWidth = 600});

  final Widget child;
  final double maxWidth;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFF4FBF4), Color(0xFFE3F4E4), Color(0xFFF8FCF7)],
        ),
      ),
      child: Stack(
        children: [
          Positioned(
              top: -90,
              right: -65,
              child: _shape(190, AppColors.accent.withValues(alpha: 0.26))),
          Positioned(
              bottom: -80,
              left: -50,
              child: _shape(170, AppColors.secondary.withValues(alpha: 0.12))),
          Positioned(
              top: 180,
              left: 18,
              child: _shape(38, AppColors.primary.withValues(alpha: 0.08))),
          Positioned(
            top: 92,
            left: 34,
            child: _illustration(Icons.eco_outlined, 52),
          ),
          Positioned(
            bottom: 54,
            right: 30,
            child: _illustration(Icons.restaurant_outlined, 58),
          ),
          SafeArea(
            child: Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: maxWidth),
                child: Padding(padding: const EdgeInsets.all(20), child: child),
              ),
            ),
          ),
        ],
      ),
    );
  }

  static Widget _shape(double size, Color color) => IgnorePointer(
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
      );

  static Widget _illustration(IconData icon, double size) => IgnorePointer(
        child: Icon(icon,
            size: size, color: AppColors.primary.withValues(alpha: 0.055)),
      );
}

class AuthSurface extends StatelessWidget {
  const AuthSurface({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.88),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withValues(alpha: 0.8)),
        boxShadow: [
          BoxShadow(
              color: AppColors.primary.withValues(alpha: 0.12),
              blurRadius: 36,
              offset: const Offset(0, 14)),
        ],
      ),
      child: child,
    );
  }
}

import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

/// Reusable scan-frame overlay drawn on top of a camera preview (or a
/// placeholder background when the camera is unavailable). Purely visual -
/// no image analysis happens here.
class ScanOverlay extends StatefulWidget {
  const ScanOverlay({super.key, this.frameSize = 280, this.cornerLength = 28, this.borderRadius = 24});

  final double frameSize;
  final double cornerLength;
  final double borderRadius;

  @override
  State<ScanOverlay> createState() => _ScanOverlayState();
}

class _ScanOverlayState extends State<ScanOverlay> with SingleTickerProviderStateMixin {
  late final AnimationController _controller =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 2200))..repeat(reverse: true);

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.frameSize,
      height: widget.frameSize,
      child: Stack(
        children: [
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(widget.borderRadius),
              boxShadow: [
                BoxShadow(color: AppColors.primary.withValues(alpha: 0.25), blurRadius: 32, spreadRadius: 2),
              ],
            ),
          ),
          CustomPaint(
            size: Size(widget.frameSize, widget.frameSize),
            painter: _CornerPainter(
              cornerLength: widget.cornerLength,
              borderRadius: widget.borderRadius,
              color: AppColors.secondary,
            ),
          ),
          AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              final top = widget.frameSize * _controller.value;
              return Positioned(
                top: top.clamp(8, widget.frameSize - 8),
                left: 16,
                right: 16,
                child: Container(
                  height: 2.5,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(2),
                    gradient: LinearGradient(
                      colors: [
                        AppColors.secondary.withValues(alpha: 0),
                        AppColors.secondary,
                        AppColors.secondary.withValues(alpha: 0),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _CornerPainter extends CustomPainter {
  _CornerPainter({required this.cornerLength, required this.borderRadius, required this.color});

  final double cornerLength;
  final double borderRadius;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final w = size.width;
    final h = size.height;
    final r = borderRadius;
    final l = cornerLength;

    void corner(Offset arcCenter, double startAngle, Offset lineStart1, Offset lineEnd1, Offset lineStart2, Offset lineEnd2) {
      canvas.drawArc(Rect.fromCircle(center: arcCenter, radius: r), startAngle, 1.5708, false, paint);
      canvas.drawLine(lineStart1, lineEnd1, paint);
      canvas.drawLine(lineStart2, lineEnd2, paint);
    }

    corner(Offset(r, r), 3.1416, Offset(0, r + l), Offset(0, r), Offset(r, 0), Offset(r + l, 0));
    corner(Offset(w - r, r), -1.5708, Offset(w - r, 0), Offset(w - r - l, 0), Offset(w, r), Offset(w, r + l));
    corner(Offset(r, h - r), 1.5708, Offset(0, h - r), Offset(0, h - r - l), Offset(r, h), Offset(r + l, h));
    corner(
      Offset(w - r, h - r),
      0,
      Offset(w, h - r),
      Offset(w, h - r - l),
      Offset(w - r, h),
      Offset(w - r - l, h),
    );
  }

  @override
  bool shouldRepaint(covariant _CornerPainter oldDelegate) => false;
}

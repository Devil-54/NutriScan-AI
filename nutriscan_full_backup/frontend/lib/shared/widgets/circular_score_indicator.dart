import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';

class CircularScoreIndicator extends StatelessWidget {
  const CircularScoreIndicator({
    super.key,
    required this.score,
    this.size = 96,
    this.strokeWidth = 9,
    this.label,
  });

  /// 0-100
  final int score;
  final double size;
  final double strokeWidth;
  final String? label;

  Color get _color {
    if (score >= 75) return AppColors.success;
    if (score >= 50) return AppColors.warning;
    return AppColors.error;
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              value: score / 100,
              strokeWidth: strokeWidth,
              strokeCap: StrokeCap.round,
              backgroundColor: _color.withValues(alpha: 0.12),
              valueColor: AlwaysStoppedAnimation<Color>(_color),
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('$score', style: AppTextStyles.headline(color: _color)),
              if (label != null) Text(label!, style: AppTextStyles.caption()),
            ],
          ),
        ],
      ),
    );
  }
}

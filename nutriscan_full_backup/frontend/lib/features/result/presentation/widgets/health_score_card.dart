import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../domain/result_dummy_data.dart';
import 'risk_badge.dart';

class HealthScoreCard extends StatefulWidget {
  const HealthScoreCard({super.key, required this.score, required this.riskLevel, required this.productName});

  final int score;
  final RiskLevel riskLevel;
  final String productName;

  @override
  State<HealthScoreCard> createState() => _HealthScoreCardState();
}

class _HealthScoreCardState extends State<HealthScoreCard> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1100),
  )..forward();
  late final Animation<double> _animation = CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic);

  Color get _scoreColor {
    if (widget.score >= 75) return AppColors.success;
    if (widget.score >= 50) return AppColors.warning;
    return AppColors.error;
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(color: _scoreColor.withValues(alpha: 0.12), blurRadius: 28, offset: const Offset(0, 14)),
        ],
      ),
      child: Column(
        children: [
          Text(widget.productName, style: AppTextStyles.title(), textAlign: TextAlign.center),
          const SizedBox(height: 20),
          SizedBox(
            width: 168,
            height: 168,
            child: AnimatedBuilder(
              animation: _animation,
              builder: (context, child) {
                final animatedScore = widget.score * _animation.value;
                return Stack(
                  alignment: Alignment.center,
                  children: [
                    SizedBox(
                      width: 168,
                      height: 168,
                      child: CircularProgressIndicator(
                        value: animatedScore / 100,
                        strokeWidth: 12,
                        strokeCap: StrokeCap.round,
                        backgroundColor: _scoreColor.withValues(alpha: 0.1),
                        valueColor: AlwaysStoppedAnimation<Color>(_scoreColor),
                      ),
                    ),
                    Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('Health Score', style: AppTextStyles.caption()),
                        const SizedBox(height: 4),
                        Text.rich(
                          TextSpan(
                            children: [
                              TextSpan(
                                text: animatedScore.round().toString(),
                                style: AppTextStyles.displayLarge(color: _scoreColor),
                              ),
                              TextSpan(text: ' / 100', style: AppTextStyles.subtext()),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                );
              },
            ),
          ),
          const SizedBox(height: 18),
          RiskBadge(riskLevel: widget.riskLevel),
        ],
      ),
    ).animate().fadeIn(duration: 350.ms).scale(begin: const Offset(0.96, 0.96), curve: Curves.easeOutCubic);
  }
}

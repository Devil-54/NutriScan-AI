import 'package:flutter/material.dart' hide StepState;
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';
import 'processing_step_widget.dart';

class ScanningProgressCard extends StatelessWidget {
  const ScanningProgressCard({
    super.key,
    required this.percentage,
    required this.steps,
    required this.currentStepIndex,
  });

  final int percentage;
  final List<String> steps;
  final int currentStepIndex;

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      child: Column(
        children: [
          Stack(
            alignment: Alignment.center,
            children: [
              // No bundled Lottie asset yet (assets/animations/ is empty) -
              // this pulsing gradient ring is the stand-in "premium AI
              // animation". Swap for Lottie.asset('assets/animations/ai_scan.json')
              // once a real animation file is added; ScanningProgressCard's
              // API doesn't need to change for that swap.
              SizedBox(
                width: 140,
                height: 140,
                child: CircularProgressIndicator(
                  value: percentage / 100,
                  strokeWidth: 10,
                  strokeCap: StrokeCap.round,
                  backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                  valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                ),
              ),
              Container(
                width: 92,
                height: 92,
                decoration: const BoxDecoration(
                  gradient: LinearGradient(colors: [AppColors.primary, AppColors.secondary]),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.auto_awesome_rounded, color: Colors.white, size: 34),
              )
                  .animate(onPlay: (c) => c.repeat(reverse: true))
                  .scale(begin: const Offset(1, 1), end: const Offset(1.08, 1.08), duration: 900.ms),
              Positioned(
                bottom: 0,
                child: Text('$percentage%', style: AppTextStyles.title(color: AppColors.primary)),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Column(
            children: [
              for (int i = 0; i < steps.length; i++)
                ProcessingStepWidget(
                  label: steps[i],
                  state: i < currentStepIndex
                      ? StepState.done
                      : i == currentStepIndex
                          ? StepState.active
                          : StepState.pending,
                ),
            ],
          ),
        ],
      ),
    );
  }
}

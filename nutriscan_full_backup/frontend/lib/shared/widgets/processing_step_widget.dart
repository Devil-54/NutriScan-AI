import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';

enum StepState { pending, active, done }

class ProcessingStepWidget extends StatelessWidget {
  const ProcessingStepWidget({super.key, required this.label, required this.state});

  final String label;
  final StepState state;

  @override
  Widget build(BuildContext context) {
    final Widget indicator = switch (state) {
      StepState.done => const Icon(Icons.check_circle_rounded, color: AppColors.success, size: 22),
      StepState.active => const SizedBox(
          width: 18,
          height: 18,
          child: CircularProgressIndicator(strokeWidth: 2.5, color: AppColors.primary),
        ),
      StepState.pending => Icon(Icons.circle_outlined, color: Colors.grey.shade300, size: 20),
    };

    final textColor = state == StepState.pending ? AppColors.subtext : AppColors.text;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          SizedBox(width: 22, child: Center(child: indicator)),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              label,
              style: state == StepState.active
                  ? AppTextStyles.bodyMedium(color: textColor)
                  : AppTextStyles.body(color: textColor),
            ),
          ),
        ],
      ),
    );
  }
}

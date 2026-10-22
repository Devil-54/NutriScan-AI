import 'package:flutter/material.dart';

import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../domain/result_dummy_data.dart';

class NutritionCard extends StatelessWidget {
  const NutritionCard({super.key, required this.fact});

  final NutritionFact fact;

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 10),
      child: Column(
        children: [
          Text(fact.emoji, style: const TextStyle(fontSize: 22)),
          const SizedBox(height: 8),
          Text.rich(
            TextSpan(
              children: [
                TextSpan(text: fact.value, style: AppTextStyles.title()),
                TextSpan(text: ' ${fact.unit}', style: AppTextStyles.caption()),
              ],
            ),
          ),
          const SizedBox(height: 2),
          Text(fact.label, style: AppTextStyles.caption()),
        ],
      ),
    );
  }
}

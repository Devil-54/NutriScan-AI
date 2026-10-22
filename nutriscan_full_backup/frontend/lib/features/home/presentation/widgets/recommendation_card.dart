import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../domain/dashboard_dummy_data.dart';

class RecommendationCard extends StatelessWidget {
  const RecommendationCard({super.key, required this.items});

  final List<RecommendationItem> items;

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.eco_outlined, color: AppColors.success, size: 20),
              const SizedBox(width: 8),
              Text('Healthy Alternatives', style: AppTextStyles.title()),
            ],
          ),
          const SizedBox(height: 14),
          for (int i = 0; i < items.length; i++) ...[
            if (i > 0) const Divider(height: 20),
            Row(
              children: [
                Text(items[i].icon, style: const TextStyle(fontSize: 22)),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(items[i].name, style: AppTextStyles.bodyMedium()),
                      Text(items[i].reason, style: AppTextStyles.caption()),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

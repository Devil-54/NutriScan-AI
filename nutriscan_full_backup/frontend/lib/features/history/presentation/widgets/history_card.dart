import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../../result/presentation/widgets/risk_badge.dart';
import '../../domain/history_dummy_data.dart';

class HistoryCard extends StatelessWidget {
  const HistoryCard({super.key, required this.entry, required this.onQuickView});

  final ScanHistoryEntry entry;
  final VoidCallback onQuickView;

  Color get _scoreColor {
    if (entry.healthScore >= 75) return AppColors.success;
    if (entry.healthScore >= 50) return AppColors.warning;
    return AppColors.error;
  }

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      onTap: onQuickView,
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
          Container(
            width: 52,
            height: 52,
            alignment: Alignment.center,
            decoration: BoxDecoration(color: _scoreColor.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(14)),
            // History responses do not include an emoji, category, or image.
            // Keep the existing leading tile without fabricating per-scan data.
            child: Icon(Icons.inventory_2_outlined, size: 24, color: _scoreColor),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(entry.name, style: AppTextStyles.bodyMedium(), maxLines: 1, overflow: TextOverflow.ellipsis),
                const SizedBox(height: 4),
                Text('Health Score: ${entry.healthScore}/100', style: AppTextStyles.caption()),
                const SizedBox(height: 6),
                RiskBadge(riskLevel: entry.riskLevel),
              ],
            ),
          ),
          Column(
            children: [
              Text('${entry.healthScore}', style: AppTextStyles.title(color: _scoreColor)),
              IconButton(
                onPressed: onQuickView,
                icon: const Icon(Icons.visibility_outlined, size: 18, color: AppColors.primary),
                tooltip: 'Quick View',
              ),
            ],
          ),
          ]),
          const SizedBox(height: 8),
          Text('Personalized Result: ${entry.personalizedSummary}', style: AppTextStyles.caption()),
          const SizedBox(height: 6),
          if (entry.concernIngredients.isEmpty)
            Text('Personalized concern: None detected for the saved profile.', style: AppTextStyles.caption())
          else ...[
            Text('Concern Ingredients / Nutrition Factors:', style: AppTextStyles.bodyMedium()),
            for (final ingredient in entry.concernIngredients)
              Text('• ${ingredient.name} — ${ingredient.explanation}', style: AppTextStyles.caption()),
          ],
          if (entry.pregnancyContext.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text('Pregnancy-aware analysis: ${entry.pregnancyContext}', style: AppTextStyles.bodyMedium()),
            Text('Focus on appropriate pregnancy nutrition and healthy weight gain.', style: AppTextStyles.caption()),
          ],
        ],
      ),
    );
  }
}

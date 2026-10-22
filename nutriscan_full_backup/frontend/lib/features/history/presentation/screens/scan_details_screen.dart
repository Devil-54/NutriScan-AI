import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/secondary_button.dart';
import '../../../history/domain/history_dummy_data.dart';
import '../providers/history_provider.dart';
import '../../../result/domain/result_dummy_data.dart';
import '../../../result/presentation/widgets/ai_recommendation_card.dart';
import '../../../result/presentation/widgets/health_score_card.dart';
import '../../../result/presentation/widgets/ingredient_card.dart';

/// Shows a past scan's full report. Reuses every Result-screen widget
/// (HealthScoreCard, IngredientCard, etc.) rather than duplicating them -
/// only the surrounding screen and the "past scan" framing are new.
/// The selected demo history entry carries its own summary and ingredients.
class ScanDetailsScreen extends ConsumerWidget {
  const ScanDetailsScreen({super.key, this.scanId});

  final String? scanId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (scanId == null || scanId!.isEmpty) {
      return const _ScanDetailsBody(entry: null);
    }
    return ref.watch(scanDetailProvider(scanId!)).when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (_, __) => Scaffold(
        appBar: const CustomAppBar(title: 'Scan Details'),
        body: Center(
          child: TextButton(
            onPressed: () => ref.invalidate(scanDetailProvider(scanId!)),
            child: const Text('Could not load this scan. Retry'),
          ),
        ),
      ),
      data: (json) => _ScanDetailsBody(entry: ScanHistoryEntry.fromApi(json)),
    );
  }
}

class _NutritionInformation extends StatelessWidget {
  const _NutritionInformation({required this.values});

  final Map<String, dynamic> values;

  static const _labels = <String, String>{
    'calories': 'Calories',
    'fat_g': 'Total Fat',
    'saturated_fat_g': 'Saturated Fat',
    'trans_fat_g': 'Trans Fat',
    'cholesterol_mg': 'Cholesterol',
    'sodium_mg': 'Sodium',
    'potassium_mg': 'Potassium',
    'calcium_mg': 'Calcium',
    'iron_mg': 'Iron',
    'carbohydrates_g': 'Total Carbohydrate',
    'fiber_g': 'Dietary Fiber',
    'protein_g': 'Protein',
    'sugar_g': 'Total Sugars',
  };

  @override
  Widget build(BuildContext context) {
    if (values.isEmpty) {
      return Text('Not available from scanned label', style: AppTextStyles.body());
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: _labels.entries.map((entry) {
        final value = values[entry.key];
        final unit = entry.key.endsWith('_mg') ? ' mg' : entry.key == 'calories' ? '' : ' g';
        return Padding(
          padding: const EdgeInsets.only(bottom: 6),
          child: Text(
            '${entry.value}: ${value ?? 'Not available from scanned label'}${value == null ? '' : unit}',
            style: AppTextStyles.body(),
          ),
        );
      }).toList(growable: false),
    );
  }
}

class _ScanDetailsBody extends StatelessWidget {
  const _ScanDetailsBody({this.entry});

  final ScanHistoryEntry? entry;

  @override
  Widget build(BuildContext context) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);
    final productName = entry?.name ?? 'Scan result unavailable';
    final healthScore = entry?.healthScore ?? 0;
    final riskLevel = entry?.riskLevel ?? RiskLevel.safe;
    final ingredients = entry?.ingredients ?? const <IngredientResult>[];

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: CustomAppBar(
        title: 'Scan Details',
        actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.ios_share_rounded))],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
              children: [
                if (entry != null) ...[
                  Text(entry!.dateLabel, style: AppTextStyles.subtext(), textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                ],
                HealthScoreCard(score: healthScore, riskLevel: riskLevel, productName: productName),
                const SizedBox(height: 28),

                if (entry?.rawOcrText?.trim().isNotEmpty == true) ...[
                  Text('Raw OCR Text', style: AppTextStyles.headline()),
                  const SizedBox(height: 8),
                  Text(entry!.rawOcrText!, style: AppTextStyles.body()),
                  const SizedBox(height: 28),
                ],

                Text('Normalized Ingredients', style: AppTextStyles.headline()),
                const SizedBox(height: 12),
                if (ingredients.isEmpty)
                  Text('Unknown / unresolved ingredient', style: AppTextStyles.body())
                else
                  for (int i = 0; i < ingredients.length; i++) ...[
                    IngredientCard(ingredient: ingredients[i]),
                    if (i != ingredients.length - 1) const SizedBox(height: 10),
                  ],
                const SizedBox(height: 28),
                Text('Concern Ingredients / Nutrition Factors', style: AppTextStyles.headline()),
                const SizedBox(height: 12),
                if (entry == null || entry!.concernIngredients.isEmpty)
                  Text('Personalized concern: None detected for the saved profile.', style: AppTextStyles.body())
                else
                  for (final ingredient in entry!.concernIngredients)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(
                        '${ingredient.name} — ${ingredient.explanation}',
                        style: AppTextStyles.body(),
                      ),
                    ),
                const SizedBox(height: 28),
                Text('Nutrition Information', style: AppTextStyles.headline()),
                const SizedBox(height: 12),
                _NutritionInformation(values: entry?.nutrition ?? const {}),
                const SizedBox(height: 28),
                Text('Personalized Analysis', style: AppTextStyles.headline()),
                const SizedBox(height: 12),
                AiRecommendationCard(
                  recommendation: entry == null
                      ? 'No saved personalized evaluation is available.'
                      : 'This result was evaluated against the health profile saved when it was scanned.',
                  reasons: entry?.reasons ?? const [],
                ),
                const SizedBox(height: 28),
                if (entry != null && entry!.triggeredRules.isNotEmpty) ...[
                  Text('Health Conditions Considered', style: AppTextStyles.headline()),
                  const SizedBox(height: 12),
                  for (final rule in entry!.triggeredRules)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text('• $rule', style: AppTextStyles.body()),
                    ),
                  const SizedBox(height: 20),
                ],
                if (entry != null && entry!.profileSnapshot.isNotEmpty) ...[
                  Text('Profile Considered at Scan Time', style: AppTextStyles.headline()),
                  const SizedBox(height: 12),
                  if (entry!.profileSnapshot['pregnant'] == true)
                    Text('Pregnancy-aware analysis: applied. Weight-loss recommendations are not applied during pregnancy.', style: AppTextStyles.body()),
                  if (entry!.profileSnapshot['pregnant'] == true)
                    Text('• Pregnancy: considered', style: AppTextStyles.body()),
                  for (final allergy in ((entry!.profileSnapshot['allergies'] as List?) ?? const []))
                    Text('• Allergy: $allergy', style: AppTextStyles.body()),
                  for (final condition in ((entry!.profileSnapshot['conditions'] as List?) ?? const []))
                    Text('• Health condition: $condition', style: AppTextStyles.body()),
                  if (entry!.profileSnapshot['fitness_goal'] != null)
                    Text('• Fitness goal: ${entry!.profileSnapshot['fitness_goal']}', style: AppTextStyles.body()),
                  const SizedBox(height: 20),
                ],
                if (entry != null && entry!.recommendations.isNotEmpty) ...[
                  Text('Personalized Recommendations', style: AppTextStyles.headline()),
                  const SizedBox(height: 12),
                  for (final recommendation in entry!.recommendations)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text('• $recommendation', style: AppTextStyles.body()),
                    ),
                  const SizedBox(height: 20),
                ],
                if (entry != null) ...[
                  Text('Scan ID: ${entry!.scanId}', style: AppTextStyles.subtext()),
                  const SizedBox(height: 20),
                ],

                SecondaryButton(label: 'Share Report', icon: Icons.ios_share_rounded, onPressed: () {}),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

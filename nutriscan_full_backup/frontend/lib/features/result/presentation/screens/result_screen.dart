import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/animation_utils.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../../../../shared/widgets/secondary_button.dart';
import '../../../home/presentation/widgets/daily_tip_card.dart';
import '../../data/recommendation_model.dart';
import '../../data/scan_analysis_payload.dart';
import '../../domain/result_dummy_data.dart';
import '../widgets/ai_recommendation_card.dart';
import '../widgets/alternative_food_card.dart';
import '../widgets/health_score_card.dart';
import '../widgets/ingredient_card.dart';

/// The premium AI Result experience. Displays the real Recommendation
/// Engine response ([result]) when available (health score, risk level,
/// ingredient warnings, AI reasons, alternatives, and health tip). The screen
/// only renders values supplied by the current recommendation.
/// It intentionally never falls back to sample product data: doing so makes
/// an incomplete or missing response look like the result of a prior scan.
class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key, this.result, this.payload});

  final RecommendationResultModel? result;
  final ScanAnalysisPayload? payload;

  RiskLevel get _riskLevel {
    if (result == null) {
      return RiskLevel.safe;
    }
    return switch (result!.riskLevel) {
      'low' => RiskLevel.lowRisk,
      'moderate' => RiskLevel.moderateRisk,
      'high' => RiskLevel.highRisk,
      'critical' => RiskLevel.unsafe,
      _ => RiskLevel.safe,
    };
  }

  String get _productName => payload?.productName?.trim().isNotEmpty == true
      ? payload!.productName!
      : 'Product not identified';

  List<IngredientResult> get _ingredientResults {
    if (result == null) {
      return const [];
    }
    final warningStatus = result!.riskLevel == 'moderate'
        ? IngredientStatus.warning
        : IngredientStatus.danger;
    final warnings = result!.ingredientWarnings.map((w) => IngredientResult(
        name: w.ingredient,
        status: warningStatus,
        explanation: w.reason));
    final safe = result!.safeFoods.map((name) => IngredientResult(
        name: name,
        status: IngredientStatus.safe,
        explanation: 'No known risk for your profile.'));
    final combined = [...warnings, ...safe];
    return combined;
  }

  String get _recommendationText {
    if (result == null) {
      return 'No recommendation data is available for this scan.';
    }
    final label = switch (result!.status) {
      'safe' => 'generally safe for your profile',
      'warning' =>
        'okay in moderation, but worth some caution for your profile',
      _ => 'not recommended for your profile',
    };
    return 'This product is $label.';
  }

  List<String> get _reasons => result?.reasons ?? const [];

  List<AlternativeFood> get _alternatives {
    if (result == null || result!.alternatives.isEmpty) {
      return const [];
    }
    return result!.alternatives
        .map((a) => AlternativeFood(name: a.suggestion, emoji: '🥗'))
        .toList();
  }

  String get _healthTip {
    if (result != null && result!.healthTips.isNotEmpty) {
      return result!.healthTips.first;
    }
    return 'Review the ingredients above before making a dietary decision.';
  }

  List<Widget> _metadataAndNutrition() {
    final nutrition = payload?.nutrition;
    final metadata = <String>[
      if (payload?.brand?.trim().isNotEmpty == true) 'Brand: ${payload!.brand}',
      if (payload?.category?.trim().isNotEmpty == true) 'Category: ${payload!.category}',
      if (payload != null) 'Scanned: ${payload!.scanTime.toLocal().toString().split('.').first}',
    ];
    final facts = <String>[
      if (nutrition?.calories != null) 'Calories: ${nutrition!.calories!.round()} kcal',
      if (nutrition?.proteinG != null) 'Protein: ${nutrition!.proteinG} g',
      if (nutrition?.sugarG != null) 'Sugar: ${nutrition!.sugarG} g',
      if (nutrition?.fatG != null) 'Fat: ${nutrition!.fatG} g',
      if (nutrition?.sodiumMg != null) 'Sodium: ${nutrition!.sodiumMg!.round()} mg',
      if (nutrition?.carbohydratesG != null) 'Carbohydrates: ${nutrition!.carbohydratesG} g',
    ];
    return [
      if (metadata.isNotEmpty) ...[
        const SizedBox(height: 16),
        Text(metadata.join(' • '), style: AppTextStyles.caption(), textAlign: TextAlign.center),
      ],
      if (facts.isNotEmpty) ...[
        const SizedBox(height: 28),
        Text('Nutrition Summary', style: AppTextStyles.headline()),
        const SizedBox(height: 10),
        Wrap(spacing: 8, runSpacing: 8, children: facts.map((fact) => Chip(label: Text(fact))).toList()),
      ],
    ];
  }

  @override
  Widget build(BuildContext context) {
    final maxWidth = ResponsiveUtils.value(context,
        mobile: double.infinity, tablet: 700.0, desktop: 900.0);
    final ingredients = _ingredientResults;
    final alternatives = _alternatives;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: CustomAppBar(
        title: 'Scan Result',
        actions: [
          IconButton(
              onPressed: () {}, icon: const Icon(Icons.ios_share_rounded))
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
              children: [
                AppAnimations.fadeSlideUp(
                  HealthScoreCard(
                    score: result?.recommendationScore ?? 0,
                    riskLevel: _riskLevel,
                    productName: _productName,
                  ),
                ),
                ..._metadataAndNutrition(),
                const SizedBox(height: 28),
                Text('Ingredients', style: AppTextStyles.headline()),
                const SizedBox(height: 12),
                for (int i = 0; i < ingredients.length; i++) ...[
                  AppAnimations.staggeredItem(
                      IngredientCard(ingredient: ingredients[i]), i),
                  if (i != ingredients.length - 1) const SizedBox(height: 10),
                ],
                const SizedBox(height: 28),
                AiRecommendationCard(
                    recommendation: _recommendationText, reasons: _reasons),
                const SizedBox(height: 28),
                Text('Healthy Alternatives', style: AppTextStyles.headline()),
                const SizedBox(height: 12),
                SizedBox(
                  height: 128,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: alternatives.length,
                    separatorBuilder: (context, index) =>
                        const SizedBox(width: 12),
                    itemBuilder: (context, i) => AlternativeFoodCard(
                        name: alternatives[i].name,
                        emoji: alternatives[i].emoji),
                  ),
                ),
                const SizedBox(height: 28),
                DailyTipCard(tip: _healthTip),
                const SizedBox(height: 32),
                PrimaryButton(
                  label: 'Scan Again',
                  icon: Icons.camera_alt_rounded,
                  onPressed: () => context.goNamed(RouteConstants.scanName),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: SecondaryButton(
                          label: 'Save',
                          icon: Icons.bookmark_outline_rounded,
                          onPressed: () {}),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: SecondaryButton(
                          label: 'Share',
                          icon: Icons.ios_share_rounded,
                          onPressed: () {}),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                SecondaryButton(
                  label: 'Back Home',
                  icon: Icons.home_rounded,
                  onPressed: () => context.goNamed(RouteConstants.homeName),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

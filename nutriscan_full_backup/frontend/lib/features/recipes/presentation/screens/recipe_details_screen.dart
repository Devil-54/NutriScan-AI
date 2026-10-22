import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../../../shared/widgets/section_header.dart';
import '../../domain/recipe_data.dart';

class RecipeDetailsScreen extends StatelessWidget {
  const RecipeDetailsScreen({super.key, required this.recipe});
  final Recipe recipe;

  @override
  Widget build(BuildContext context) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: CustomAppBar(title: recipe.name),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
              children: [
                Text(recipe.description, style: AppTextStyles.body()),
                const SizedBox(height: 24),
                const SectionHeader(title: 'Ingredients'),
                const SizedBox(height: 12),
                CustomCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  for (final ingredient in recipe.ingredients) Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text('• $ingredient', style: AppTextStyles.body()),
                  ),
                ])),
                const SizedBox(height: 24),
                const SectionHeader(title: 'Preparation'),
                const SizedBox(height: 12),
                CustomCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  for (int i = 0; i < recipe.steps.length; i++) Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text('${i + 1}. ${recipe.steps[i]}', style: AppTextStyles.body()),
                  ),
                ])),
                const SizedBox(height: 24),
                const SectionHeader(title: 'Nutrition per serving'),
                const SizedBox(height: 12),
                CustomCard(child: Wrap(spacing: 22, runSpacing: 14, children: [
                  _NutritionValue(label: 'Calories', value: '${recipe.calories} kcal'),
                  _NutritionValue(label: 'Protein', value: '${recipe.protein} g'),
                  _NutritionValue(label: 'Carbohydrates', value: '${recipe.carbohydrates} g'),
                  _NutritionValue(label: 'Fat', value: '${recipe.fat} g'),
                  _NutritionValue(label: 'Fibre', value: '${recipe.fibre} g'),
                ])),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _NutritionValue extends StatelessWidget {
  const _NutritionValue({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 115,
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(value, style: AppTextStyles.title(color: AppColors.primary)),
      const SizedBox(height: 2),
      Text(label, style: AppTextStyles.caption()),
    ]),
  );
}

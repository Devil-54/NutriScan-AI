import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../../../shared/widgets/section_header.dart';
import '../../domain/recipe_data.dart';

class RecipesScreen extends StatelessWidget {
  const RecipesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Recipes', showBackButton: false),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
              children: [
                for (final category in ['Breakfast', 'Lunch', 'Dinner']) ...[
                  SectionHeader(title: category.toUpperCase()),
                  const SizedBox(height: 12),
                  for (final recipe in recipes.where((recipe) => recipe.category == category)) ...[
                    _RecipeCard(recipe: recipe),
                    const SizedBox(height: 12),
                  ],
                  const SizedBox(height: 12),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RecipeCard extends StatelessWidget {
  const _RecipeCard({required this.recipe});
  final Recipe recipe;

  @override
  Widget build(BuildContext context) => CustomCard(
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(recipe.name, style: AppTextStyles.title()),
      const SizedBox(height: 6),
      Text(recipe.description, style: AppTextStyles.subtext()),
      const SizedBox(height: 14),
      Row(children: [
        _NutritionLabel(label: '${recipe.calories} kcal'),
        const SizedBox(width: 16),
        _NutritionLabel(label: '${recipe.protein}g protein'),
        const Spacer(),
        TextButton(
          onPressed: () => context.pushNamed(RouteConstants.recipeDetailsName, extra: recipe),
          child: const Text('View Recipe'),
        ),
      ]),
    ]),
  );
}

class _NutritionLabel extends StatelessWidget {
  const _NutritionLabel({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) => Text(label, style: AppTextStyles.caption(color: AppColors.primary));
}

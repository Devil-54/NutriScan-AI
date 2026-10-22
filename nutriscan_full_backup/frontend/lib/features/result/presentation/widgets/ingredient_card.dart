import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../domain/result_dummy_data.dart';

class IngredientCard extends StatefulWidget {
  const IngredientCard({super.key, required this.ingredient});

  final IngredientResult ingredient;

  @override
  State<IngredientCard> createState() => _IngredientCardState();
}

class _IngredientCardState extends State<IngredientCard> {
  bool _expanded = false;

  Color get _color => switch (widget.ingredient.status) {
        IngredientStatus.safe => AppColors.success,
        IngredientStatus.warning => AppColors.warning,
        IngredientStatus.danger => AppColors.error,
      };

  String get _statusLabel => switch (widget.ingredient.status) {
        IngredientStatus.safe => 'Safe',
        IngredientStatus.warning => 'Warning',
        IngredientStatus.danger => 'Danger',
      };

  IconData get _icon => switch (widget.ingredient.status) {
        IngredientStatus.safe => Icons.check_circle_rounded,
        IngredientStatus.warning => Icons.error_rounded,
        IngredientStatus.danger => Icons.dangerous_rounded,
      };

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      onTap: () => setState(() => _expanded = !_expanded),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(_icon, color: _color, size: 22),
              const SizedBox(width: 12),
              Expanded(child: Text(widget.ingredient.name, style: AppTextStyles.bodyMedium())),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: _color.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(12)),
                child: Text(_statusLabel, style: AppTextStyles.caption(color: _color)),
              ),
              const SizedBox(width: 6),
              AnimatedRotation(
                turns: _expanded ? 0.5 : 0,
                duration: const Duration(milliseconds: 200),
                child: const Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.subtext),
              ),
            ],
          ),
          AnimatedCrossFade(
            firstChild: const SizedBox(width: double.infinity),
            secondChild: Padding(
              padding: const EdgeInsets.only(top: 10, left: 34),
              child: Text(widget.ingredient.explanation, style: AppTextStyles.subtext()),
            ),
            crossFadeState: _expanded ? CrossFadeState.showSecond : CrossFadeState.showFirst,
            duration: const Duration(milliseconds: 200),
          ),
        ],
      ),
    );
  }
}

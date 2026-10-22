import 'package:flutter/material.dart';

import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';

/// A form dropdown with the same visual language as [CustomTextField].
class CustomSelectField extends StatefulWidget {
  const CustomSelectField({
    super.key,
    required this.label,
    required this.items,
    required this.onChanged,
    this.value,
    this.hint,
    this.prefixIcon,
    this.validator,
  });

  final String label;
  final String? value;
  final String? hint;
  final IconData? prefixIcon;
  final List<DropdownMenuItem<String>> items;
  final ValueChanged<String?> onChanged;
  final String? Function(String?)? validator;

  @override
  State<CustomSelectField> createState() => _CustomSelectFieldState();
}

class _CustomSelectFieldState extends State<CustomSelectField> {
  bool _isOpen = false;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final borderColor = _isOpen
        ? AppColors.primary
        : colors.outlineVariant;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      curve: Curves.easeOut,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(18),
        boxShadow: _isOpen
            ? [
                BoxShadow(
                  color: AppColors.primary.withValues(alpha: 0.14),
                  blurRadius: 16,
                  offset: const Offset(0, 5),
                ),
              ]
            : null,
      ),
      child: DropdownButtonFormField<String>(
        initialValue: widget.value,
        isExpanded: true,
        icon: AnimatedRotation(
          turns: _isOpen ? 0.5 : 0,
          duration: const Duration(milliseconds: 180),
          child: Icon(Icons.keyboard_arrow_down_rounded,
              color: _isOpen ? AppColors.primary : colors.onSurfaceVariant),
        ),
        decoration: InputDecoration(
          labelText: widget.label,
          floatingLabelBehavior: FloatingLabelBehavior.auto,
          labelStyle: AppTextStyles.bodyMedium(
              color: _isOpen ? AppColors.primary : colors.onSurfaceVariant),
          prefixIcon: widget.prefixIcon == null
              ? null
              : Icon(widget.prefixIcon,
                  color: _isOpen ? AppColors.primary : colors.onSurfaceVariant,
                  size: 21),
          filled: true,
          fillColor: colors.surface.withValues(alpha: _isOpen ? 1 : 0.92),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 18, vertical: 19),
          border: _border(borderColor),
          enabledBorder: _border(borderColor),
          focusedBorder: _border(AppColors.primary, width: 1.8),
          errorBorder: _border(AppColors.error, width: 1.5),
          focusedErrorBorder: _border(AppColors.error, width: 1.8),
          errorStyle: AppTextStyles.caption(color: AppColors.error),
        ),
        dropdownColor: colors.surface,
        borderRadius: BorderRadius.circular(16),
        style: AppTextStyles.body(color: colors.onSurface).copyWith(fontSize: 15),
        hint: Text(widget.hint ?? 'Select ${widget.label}',
            style: AppTextStyles.body(color: colors.onSurfaceVariant)),
        items: widget.items,
        onTap: () => setState(() => _isOpen = true),
        onChanged: (value) {
          setState(() => _isOpen = false);
          widget.onChanged(value);
        },
        validator: widget.validator,
      ),
    );
  }

  OutlineInputBorder _border(Color color, {double width = 1}) =>
      OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: BorderSide(color: color, width: width),
      );
}

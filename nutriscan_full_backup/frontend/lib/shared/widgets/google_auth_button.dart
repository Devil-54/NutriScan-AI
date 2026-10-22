import 'package:flutter/material.dart';

import '../../core/theme/app_text_styles.dart';

/// UI-only social auth button. No auth logic wired - onPressed is provided
/// by the caller and currently unused by any screen (Phase 4B scope).
class GoogleAuthButton extends StatelessWidget {
  const GoogleAuthButton({super.key, required this.label, this.onPressed});

  final String label;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          foregroundColor: Theme.of(context).colorScheme.onSurface,
          side: BorderSide(color: Colors.grey.shade300, width: 1.5),
          backgroundColor: Theme.of(context).colorScheme.surface,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Simple "G" glyph avoids bundling a Google-brand asset in this phase.
            Container(
              width: 20,
              height: 20,
              alignment: Alignment.center,
              decoration: const BoxDecoration(shape: BoxShape.circle, color: Color(0xFFF1F5F9)),
              child: const Text(
                'G',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF2E7DFF)),
              ),
            ),
            const SizedBox(width: 10),
            Text(label, style: AppTextStyles.bodyMedium(color: Theme.of(context).colorScheme.onSurface)),
          ],
        ),
      ),
    );
  }
}

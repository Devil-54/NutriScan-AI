import 'package:flutter/widgets.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Small set of reusable, subtle animation presets (per Phase 4A scope:
/// "prepare utilities, do not add heavy animations yet"). Feature screens
/// call these as extension-style helpers instead of hand-rolling
/// .animate() chains, keeping motion consistent app-wide.
class AppAnimations {
  AppAnimations._();

  static const Duration fast = Duration(milliseconds: 200);
  static const Duration normal = Duration(milliseconds: 350);
  static const Duration slow = Duration(milliseconds: 500);

  static Widget fadeIn(Widget child, {Duration? duration, Duration delay = Duration.zero}) {
    return child.animate().fadeIn(duration: duration ?? normal, delay: delay);
  }

  static Widget fadeSlideUp(Widget child, {Duration? duration, Duration delay = Duration.zero}) {
    return child
        .animate()
        .fadeIn(duration: duration ?? normal, delay: delay)
        .slideY(begin: 0.08, end: 0, duration: duration ?? normal, delay: delay, curve: Curves.easeOutCubic);
  }

  static Widget scaleIn(Widget child, {Duration? duration, Duration delay = Duration.zero}) {
    return child
        .animate()
        .fadeIn(duration: duration ?? fast, delay: delay)
        .scale(begin: const Offset(0.95, 0.95), end: const Offset(1, 1), duration: duration ?? fast, delay: delay);
  }

  /// Staggers fadeSlideUp across a list of items (e.g. a card list on a
  /// results/home screen) by index.
  static Widget staggeredItem(Widget child, int index, {Duration step = const Duration(milliseconds: 60)}) {
    return fadeSlideUp(child, delay: step * index);
  }
}

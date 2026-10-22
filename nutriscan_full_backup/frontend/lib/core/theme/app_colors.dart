import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  static const Color primary = Color(0xFF2E7D32);
  static const Color secondary = Color(0xFF66BB6A);
  static const Color accent = Color(0xFFA5D6A7);

  static const Color success = Color(0xFF34C759);
  static const Color warning = Color(0xFFFFB020);
  static const Color error = Color(0xFFFF4D4F);

  static const Color background = Color(0xFFF5FBF5);
  static const Color card = Color(0xFFFFFFFF);

  static const Color text = Color(0xFF1E293B);
  static const Color subtext = Color(0xFF64748B);

  // Dark theme counterparts
  static const Color backgroundDark = Color(0xFF0F172A);
  static const Color cardDark = Color(0xFF1E293B);
  static const Color textDark = Color(0xFFF1F5F9);
  static const Color subtextDark = Color(0xFF94A3B8);

  // Semantic aliases matching the Medical Rule Engine's verdict states,
  // so result screens can map status -> color with zero branching logic.
  static const Color statusSafe = success;
  static const Color statusWarning = warning;
  static const Color statusUnsafe = error;
}

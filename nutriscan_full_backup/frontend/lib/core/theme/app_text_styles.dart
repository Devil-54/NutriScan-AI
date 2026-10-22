import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Centralized text styles. Screens should reference these rather than
/// building TextStyle/GoogleFonts.poppins() inline, so typography stays
/// consistent and themeable from one place.
class AppTextStyles {
  AppTextStyles._();

  static TextStyle _base({
    required double fontSize,
    required FontWeight fontWeight,
    Color? color,
    double? height,
    double? letterSpacing,
  }) {
    return GoogleFonts.poppins(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color,
      height: height,
      letterSpacing: letterSpacing,
    );
  }

  static TextStyle displayLarge({Color? color}) =>
      _base(fontSize: 32, fontWeight: FontWeight.w700, color: color, height: 1.2);

  static TextStyle displaySmall({Color? color}) =>
      _base(fontSize: 24, fontWeight: FontWeight.w700, color: color, height: 1.25);

  static TextStyle headline({Color? color}) =>
      _base(fontSize: 20, fontWeight: FontWeight.w600, color: color, height: 1.3);

  static TextStyle title({Color? color}) =>
      _base(fontSize: 16, fontWeight: FontWeight.w600, color: color, height: 1.4);

  static TextStyle body({Color? color}) =>
      _base(fontSize: 14, fontWeight: FontWeight.w400, color: color, height: 1.5);

  static TextStyle bodyMedium({Color? color}) =>
      _base(fontSize: 14, fontWeight: FontWeight.w500, color: color, height: 1.5);

  static TextStyle subtext({Color? color}) =>
      _base(fontSize: 13, fontWeight: FontWeight.w400, color: color, height: 1.4);

  static TextStyle caption({Color? color}) =>
      _base(fontSize: 12, fontWeight: FontWeight.w400, color: color, height: 1.3);

  static TextStyle button({Color color = Colors.white}) =>
      _base(fontSize: 15, fontWeight: FontWeight.w600, color: color, letterSpacing: 0.2);
}

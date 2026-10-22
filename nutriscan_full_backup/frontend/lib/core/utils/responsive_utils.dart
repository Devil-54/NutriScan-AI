import 'package:flutter/widgets.dart';

import '../constants/app_constants.dart';

enum DeviceType { mobile, tablet, desktop }

class ResponsiveUtils {
  ResponsiveUtils._();

  static DeviceType deviceTypeOf(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    if (width >= AppConstants.tabletBreakpoint) return DeviceType.desktop;
    if (width >= AppConstants.mobileBreakpoint) return DeviceType.tablet;
    return DeviceType.mobile;
  }

  static bool isMobile(BuildContext context) => deviceTypeOf(context) == DeviceType.mobile;
  static bool isTablet(BuildContext context) => deviceTypeOf(context) == DeviceType.tablet;
  static bool isDesktop(BuildContext context) => deviceTypeOf(context) == DeviceType.desktop;

  /// Content max-width so wide screens (tablet/desktop) don't stretch
  /// forms/cards edge-to-edge.
  static double contentMaxWidth(BuildContext context) {
    switch (deviceTypeOf(context)) {
      case DeviceType.mobile:
        return double.infinity;
      case DeviceType.tablet:
        return 560;
      case DeviceType.desktop:
        return 720;
    }
  }

  /// Generic responsive value picker, e.g.
  /// ResponsiveUtils.value(context, mobile: 1, tablet: 2, desktop: 3)
  static T value<T>(
    BuildContext context, {
    required T mobile,
    T? tablet,
    T? desktop,
  }) {
    switch (deviceTypeOf(context)) {
      case DeviceType.mobile:
        return mobile;
      case DeviceType.tablet:
        return tablet ?? mobile;
      case DeviceType.desktop:
        return desktop ?? tablet ?? mobile;
    }
  }
}

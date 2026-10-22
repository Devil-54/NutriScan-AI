import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../theme/app_colors.dart';
import '../../features/history/presentation/providers/history_provider.dart';

/// Renders the persistent bottom NavigationBar around the 5 tab branches
/// (Home, Scan, History, Profile, Recipes). Each branch keeps its own
/// navigation stack via go_router's StatefulShellRoute - switching tabs
/// doesn't rebuild/lose state in the other tabs. Navigation UI only, per
/// Phase 4C scope - no auth/route guarding logic here.
class MainShell extends StatelessWidget {
  const MainShell({super.key, required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  static const _destinations = [
    NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home_rounded), label: 'Home'),
    NavigationDestination(
      icon: Icon(Icons.camera_alt_outlined),
      selectedIcon: Icon(Icons.camera_alt_rounded),
      label: 'Scan',
    ),
    NavigationDestination(
      icon: Icon(Icons.history_outlined),
      selectedIcon: Icon(Icons.history_rounded),
      label: 'History',
    ),
    NavigationDestination(
      icon: Icon(Icons.person_outline_rounded),
      selectedIcon: Icon(Icons.person_rounded),
      label: 'Profile',
    ),
    NavigationDestination(
      icon: Icon(Icons.menu_book_outlined),
      selectedIcon: Icon(Icons.menu_book_rounded),
      label: 'Recipes',
    ),
  ];

  void _onDestinationSelected(BuildContext context, int index) {
    if (index == 2) {
      // A StatefulShellRoute keeps the History widget alive.  Refresh its
      // server-backed provider every time the user enters the tab.
      ProviderScope.containerOf(context).invalidate(scanHistoryProvider);
    }
    navigationShell.goBranch(
      index,
      // Tapping the already-active tab pops it back to its root, matching
      // standard mobile bottom-nav behavior.
      initialLocation: index == navigationShell.currentIndex,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBarTheme(
        data: NavigationBarThemeData(
          backgroundColor: Theme.of(context).colorScheme.surface,
          indicatorColor: AppColors.primary.withValues(alpha: 0.12),
          labelTextStyle: WidgetStateProperty.all(
            const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
          ),
        ),
        child: NavigationBar(
          selectedIndex: navigationShell.currentIndex,
          onDestinationSelected: (index) => _onDestinationSelected(context, index),
          destinations: _destinations,
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';

import 'custom_app_bar.dart';

/// Temporary scaffold used by Phase 4A routes until each feature's real UI
/// is built in later phases. Not a reusable "component" per se - just wiring.
class PlaceholderScreen extends StatelessWidget {
  const PlaceholderScreen({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(title: title),
      body: Center(
        child: Text(
          '$title screen',
          style: Theme.of(context).textTheme.titleMedium,
        ),
      ),
    );
  }
}

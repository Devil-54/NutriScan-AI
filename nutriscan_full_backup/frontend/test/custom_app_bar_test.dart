import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:nutriscan_app/shared/widgets/custom_app_bar.dart';

void main() {
  GoRouter buildRouter({required String initialLocation}) {
    return GoRouter(
      initialLocation: initialLocation,
      routes: [
        GoRoute(
          path: '/home',
          name: 'home',
          builder: (context, state) => const Scaffold(body: Center(child: Text('Home'))),
        ),
        GoRoute(
          path: '/details',
          name: 'details',
          builder: (context, state) => const Scaffold(
            appBar: CustomAppBar(title: 'Details'),
            body: Center(child: Text('Details')),
          ),
        ),
      ],
    );
  }

  testWidgets('returns to the previous route when one exists', (tester) async {
    final router = buildRouter(initialLocation: '/home');
    await tester.pumpWidget(MaterialApp.router(routerConfig: router));

    router.push('/details');
    await tester.pumpAndSettle();
    await tester.tap(find.byTooltip('Back'));
    await tester.pumpAndSettle();

    expect(find.text('Home'), findsOneWidget);
  });

  testWidgets('falls back to Home when there is no previous route', (tester) async {
    final router = buildRouter(initialLocation: '/details');
    await tester.pumpWidget(MaterialApp.router(routerConfig: router));

    await tester.tap(find.byTooltip('Back'));
    await tester.pumpAndSettle();

    expect(find.text('Home'), findsOneWidget);
  });
}

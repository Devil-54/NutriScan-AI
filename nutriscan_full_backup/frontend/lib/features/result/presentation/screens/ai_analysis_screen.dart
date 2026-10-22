import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/network/api_exception.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/app_error_widget.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/scanning_progress_card.dart';
import '../../../history/presentation/providers/history_provider.dart';
import '../../../profile/presentation/providers/profile_provider.dart';
import '../providers/result_provider.dart';
import '../../data/scan_analysis_payload.dart';

const _steps = [
  'Recognizing Nutrition...',
  'Checking Allergens...',
  'Consulting Knowledge Graph...',
  'Running Medical Rules...',
  'Generating AI Recommendation...',
];

/// AI Analysis Progress Screen. Runs the real Ingredient Parser +
/// Recommendation Engine pipeline against [ocrText] (from OCR Processing)
/// and hands the result to the Result screen via route `extra`.
class AiAnalysisScreen extends ConsumerStatefulWidget {
  const AiAnalysisScreen({super.key, this.payload});

  final ScanAnalysisPayload? payload;

  @override
  ConsumerState<AiAnalysisScreen> createState() => _AiAnalysisScreenState();
}

class _AiAnalysisScreenState extends ConsumerState<AiAnalysisScreen> {
  int _stepIndex = 0;
  String? _error;

  @override
  void initState() {
    super.initState();
    _run();
  }

  @override
  void didUpdateWidget(covariant AiAnalysisScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.payload?.scanId != widget.payload?.scanId) {
      _run();
    }
  }

  Future<void> _run() async {
    setState(() {
      _error = null;
      _stepIndex = 0;
    });

    try {
      setState(() => _stepIndex = 1);
      final parserRepo = ref.read(parserRepositoryProvider);
      final ingredients =
          await parserRepo.parseIngredients(widget.payload?.ocrText ?? '');
      if (!mounted) return;
      if (ingredients.isEmpty) {
        throw const FormatException(
            'We could not identify ingredients from this label. Please retake the photo with the ingredient list in focus.');
      }

      setState(() => _stepIndex = 2);
      final recommendationRepo = ref.read(recommendationRepositoryProvider);
      final payload = widget.payload;
      if (payload == null) {
        throw const FormatException('A scan is required before personalized analysis can run.');
      }
      final result = await recommendationRepo.generate(
        ingredients,
        scanId: payload.scanId,
        productName: payload.productName,
        nutrition: payload.nutrition,
      );

      if (!mounted) return;
      setState(() => _stepIndex = 3);
      await Future.delayed(const Duration(milliseconds: 350));

      if (mounted) {
        // The evaluation is now persisted, so both screens reload the same
        // authenticated scan source instead of incrementing local counters.
        ref.invalidate(scanHistoryProvider);
        ref.invalidate(profileStatsProvider);
        context.goNamed(RouteConstants.resultName,
            extra: (result, widget.payload));
      }
    } catch (e) {
      final message = e is ApiException
          ? e.message
          : e is Exception
              ? e.toString()
              : 'Could not complete the AI analysis. Please try again.';
      if (mounted) setState(() => _error = message);
    }
  }

  @override
  Widget build(BuildContext context) {
    final percentage = (((_stepIndex + 1) / _steps.length) * 100).round();

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'AI Analysis'),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(
                maxWidth: ResponsiveUtils.contentMaxWidth(context)),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: _error != null
                  ? AppErrorWidget(
                      message: _error,
                      onRetry: _run,
                      onChooseAnotherImage: () =>
                          context.goNamed(RouteConstants.galleryPickerName),
                      onBackToHome: () =>
                          context.goNamed(RouteConstants.homeName),
                    )
                  : Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('Consulting Our AI',
                                style: AppTextStyles.displaySmall(),
                                textAlign: TextAlign.center)
                            .animate()
                            .fadeIn(duration: 300.ms),
                        const SizedBox(height: 8),
                        Text(
                          'Cross-checking ingredients against your health profile and our Knowledge Graph.',
                          style: AppTextStyles.subtext(),
                          textAlign: TextAlign.center,
                        ).animate().fadeIn(duration: 300.ms, delay: 80.ms),
                        const SizedBox(height: 32),
                        ScanningProgressCard(
                                percentage: percentage,
                                steps: _steps,
                                currentStepIndex: _stepIndex)
                            .animate()
                            .fadeIn(duration: 350.ms, delay: 120.ms)
                            .slideY(begin: 0.06, end: 0),
                      ],
                    ),
            ),
          ),
        ),
      ),
    );
  }
}

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
import '../providers/scan_provider.dart';
import '../../../../shared/widgets/scanning_progress_card.dart';
import '../../../result/presentation/providers/result_provider.dart';
import '../../../result/data/scan_analysis_payload.dart';

const _steps = [
  'Preparing Image...',
  'Reading Food Label...',
  'Extracting Ingredients...'
];

/// OCR Processing Screen. Runs the real upload + OCR pipeline against an
/// image selected by the user and hands its extracted text to analysis.
class ScanningScreen extends ConsumerStatefulWidget {
  const ScanningScreen({super.key, this.imagePath});

  final String? imagePath;

  @override
  ConsumerState<ScanningScreen> createState() => _ScanningScreenState();
}

class _ScanningScreenState extends ConsumerState<ScanningScreen> {
  int _stepIndex = 0;
  String? _error;
  String? _scanId;

  @override
  void initState() {
    super.initState();
    _run();
  }

  @override
  void didUpdateWidget(covariant ScanningScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.imagePath != widget.imagePath) {
      // A different image must start a new scan. Retries of the same image
      // deliberately retain this ID so they resume with OCR instead of
      // uploading a duplicate scan.
      _scanId = null;
      _run();
    }
  }

  Future<void> _run() async {
    setState(() {
      _error = null;
      _stepIndex = 0;
    });

    try {
      if (widget.imagePath == null) {
        throw const FormatException(
          'Choose a readable food-label image before starting a scan.',
        );
      }

      final scanRepo = ref.read(scanRepositoryProvider);
      final ocrRepo = ref.read(ocrRepositoryProvider);

      final scanId = _scanId ?? await scanRepo.uploadScan(widget.imagePath!);
      _scanId = scanId;
      if (!mounted) return;
      setState(() => _stepIndex = 1);

      final ocrResult = await ocrRepo.process(scanId);
      if (!mounted) return;
      setState(() => _stepIndex = 2);
      await Future.delayed(const Duration(milliseconds: 350));

      if (mounted) {
        context.goNamed(
          RouteConstants.aiAnalysisName,
          extra: ScanAnalysisPayload(
            scanId: scanId,
            ocrText: ocrResult.ingredientsText,
            productName: ocrResult.productName,
            brand: ocrResult.brand,
            category: ocrResult.category,
            nutrition: ocrResult.nutrition,
            scanTime: DateTime.now(),
          ),
        );
      }
    } catch (e) {
      String message;
      if (e is ApiException) {
        if (e.code == 'DUPLICATE_UPLOAD') {
          message =
              'This photo has already been scanned. Please choose another image or review your scan history.';
        } else {
          message = e.message;
        }
      } else if (e is Exception) {
        message = e.toString();
      } else {
        message = 'Could not process this image. Please try again.';
      }
      if (mounted) setState(() => _error = message);
    }
  }

  @override
  Widget build(BuildContext context) {
    final percentage = (((_stepIndex + 1) / _steps.length) * 100).round();

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Analyzing Scan'),
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
                        Text('Analyzing Your Food',
                                style: AppTextStyles.displaySmall(),
                                textAlign: TextAlign.center)
                            .animate()
                            .fadeIn(duration: 300.ms),
                        const SizedBox(height: 8),
                        Text(
                          'Our AI is reading the label and cross-checking it with your health profile.',
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

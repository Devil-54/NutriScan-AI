import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../widgets/camera_bottom_bar.dart';
import '../widgets/camera_top_bar.dart';
import '../widgets/scan_overlay.dart';

class CameraPreviewScreen extends StatefulWidget {
  const CameraPreviewScreen({super.key});

  @override
  State<CameraPreviewScreen> createState() => _CameraPreviewScreenState();
}

class _CameraPreviewScreenState extends State<CameraPreviewScreen> {
  CameraController? _controller;
  List<CameraDescription> _cameras = [];
  int _cameraIndex = 0;
  bool _isFlashOn = false;
  bool _isCapturing = false;
  bool _isInitializing = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras.isEmpty) {
        setState(() {
          _errorMessage = 'No camera was found on this device.';
          _isInitializing = false;
        });
        return;
      }
      await _startController(_cameras[_cameraIndex]);
    } catch (e) {
      // Covers permission-denied, no hardware, or plugin-unavailable cases
      // (e.g. running in an environment without a real camera) - handled
      // as a graceful in-UI state rather than a crash.
      setState(() {
        _errorMessage =
            'Camera is unavailable. You can still choose a photo from your gallery.';
        _isInitializing = false;
      });
    }
  }

  Future<void> _startController(CameraDescription description) async {
    final controller = CameraController(description, ResolutionPreset.high,
        enableAudio: false);
    await controller.initialize();
    if (!mounted) return;
    setState(() {
      _controller = controller;
      _isInitializing = false;
      _errorMessage = null;
    });
  }

  Future<void> _toggleFlash() async {
    if (_controller == null) return;
    final next = !_isFlashOn;
    await _controller!.setFlashMode(next ? FlashMode.torch : FlashMode.off);
    setState(() => _isFlashOn = next);
  }

  Future<void> _switchCamera() async {
    if (_cameras.length < 2 || _controller == null) return;
    _cameraIndex = (_cameraIndex + 1) % _cameras.length;
    await _controller!.dispose();
    setState(() => _isInitializing = true);
    await _startController(_cameras[_cameraIndex]);
  }

  Future<void> _capture() async {
    setState(() => _isCapturing = true);
    String? imagePath;
    try {
      if (_controller != null && _controller!.value.isInitialized) {
        final file = await _controller!.takePicture();
        imagePath = file.path;
      }
    } catch (_) {
      // Fall through with imagePath == null - ImagePreviewScreen shows a
      // placeholder in that case rather than blocking the demo flow.
    }
    if (!mounted) return;
    setState(() => _isCapturing = false);
    context.pushNamed(RouteConstants.imagePreviewName, extra: imagePath);
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: const CustomAppBar(title: 'Camera'),
      body: SafeArea(
        child: Stack(
          fit: StackFit.expand,
          children: [
            _buildBackground(),
            const Center(child: ScanOverlay()),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Column(
                children: [
                  CameraTopBar(
                    isFlashOn: _isFlashOn,
                    onFlashToggle: _toggleFlash,
                    onClose: () => context.pop(),
                    onHelp: () => _showHelp(context),
                  ),
                  const Spacer(),
                  if (_errorMessage == null)
                    Text(
                      'Align the ingredient label within the frame',
                      style: AppTextStyles.body(color: Colors.white70),
                      textAlign: TextAlign.center,
                    ),
                  const SizedBox(height: 20),
                  CameraBottomBar(
                    onGalleryTap: () =>
                        context.pushNamed(RouteConstants.galleryPickerName),
                    onCaptureTap: _capture,
                    onSwitchCameraTap: _switchCamera,
                    isCapturing: _isCapturing,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBackground() {
    if (_isInitializing) {
      return const ColoredBox(
        color: Colors.black,
        child:
            Center(child: CircularProgressIndicator(color: AppColors.primary)),
      );
    }
    if (_errorMessage != null) {
      return ColoredBox(
        color: Colors.black,
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.videocam_off_rounded,
                    color: Colors.white54, size: 48),
                const SizedBox(height: 16),
                Text(_errorMessage!,
                    style: AppTextStyles.body(color: Colors.white70),
                    textAlign: TextAlign.center),
                const SizedBox(height: 24),
                PrimaryButton(
                  label: 'Choose From Gallery',
                  isFullWidth: false,
                  onPressed: () =>
                      context.pushNamed(RouteConstants.galleryPickerName),
                ),
              ],
            ),
          ),
        ),
      );
    }
    if (_controller != null && _controller!.value.isInitialized) {
      return CameraPreview(_controller!);
    }
    return const ColoredBox(color: Colors.black);
  }

  void _showHelp(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.card,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Scanning Tips', style: AppTextStyles.title()),
            const SizedBox(height: 12),
            Text(
              '• Use good lighting\n• Keep the label flat and in focus\n• Fill the frame with the ingredient list',
              style: AppTextStyles.body(color: AppColors.subtext),
            ),
          ],
        ),
      ),
    );
  }
}

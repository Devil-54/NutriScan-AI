import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../core/utils/validators.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../providers/auth_provider.dart';

class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _submitted = false;
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _handleReset() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      // Backend always returns success regardless of whether the email
      // exists (anti-enumeration) - so any non-error response means "sent".
      await ref
          .read(authProvider.notifier)
          .forgotPassword(_emailController.text.trim());
      if (mounted) setState(() => _submitted = true);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Reset Password'),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(
                maxWidth: ResponsiveUtils.contentMaxWidth(context)),
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.08),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.lock_reset_rounded,
                        color: AppColors.primary, size: 32),
                  )
                      .animate()
                      .fadeIn(duration: 300.ms)
                      .scale(begin: const Offset(0.85, 0.85)),
                  const SizedBox(height: 24),
                  Text('Forgot Password?', style: AppTextStyles.displaySmall())
                      .animate()
                      .fadeIn(duration: 300.ms, delay: 80.ms),
                  const SizedBox(height: 8),
                  Text(
                    "Enter the email linked to your account and we'll send you a reset link.",
                    style: AppTextStyles.subtext(),
                  ).animate().fadeIn(duration: 300.ms, delay: 130.ms),
                  const SizedBox(height: 32),
                  if (_error != null) ...[
                    CustomCard(
                      color: AppColors.error.withValues(alpha: 0.08),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline_rounded,
                              color: AppColors.error),
                          const SizedBox(width: 12),
                          Expanded(
                              child:
                                  Text(_error!, style: AppTextStyles.body())),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                  if (!_submitted) ...[
                    Form(
                      key: _formKey,
                      child: CustomTextField(
                        controller: _emailController,
                        label: 'Email',
                        hint: 'you@example.com',
                        prefixIcon: Icons.mail_outline_rounded,
                        keyboardType: TextInputType.emailAddress,
                        validator: Validators.email,
                        textInputAction: TextInputAction.done,
                      ),
                    )
                        .animate()
                        .fadeIn(duration: 300.ms, delay: 180.ms)
                        .slideY(begin: 0.1, end: 0),
                    const SizedBox(height: 28),
                    PrimaryButton(
                            label: 'Reset Password',
                            isLoading: _isLoading,
                            onPressed: _handleReset)
                        .animate()
                        .fadeIn(duration: 300.ms, delay: 230.ms),
                  ] else
                    CustomCard(
                      color: AppColors.success.withValues(alpha: 0.08),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle_rounded,
                              color: AppColors.success),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'If an account exists for ${_emailController.text}, a reset link is on its way.',
                              style: AppTextStyles.body(),
                            ),
                          ),
                        ],
                      ),
                    )
                        .animate()
                        .fadeIn(duration: 300.ms)
                        .slideY(begin: 0.08, end: 0),
                  const SizedBox(height: 24),
                  Center(
                    child: TextButton.icon(
                      onPressed: () =>
                          context.goNamed(RouteConstants.loginName),
                      icon: const Icon(Icons.arrow_back_rounded,
                          size: 18, color: AppColors.primary),
                      label: Text('Back to Login',
                          style: AppTextStyles.bodyMedium(
                              color: AppColors.primary)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

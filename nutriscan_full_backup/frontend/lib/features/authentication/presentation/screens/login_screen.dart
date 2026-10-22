import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/network/api_exception.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/validators.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/google_auth_button.dart';
import '../../../../shared/widgets/or_divider.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../providers/auth_provider.dart';
import '../widgets/auth_footer_link.dart';
import '../widgets/auth_header.dart';
import '../widgets/auth_page_layout.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _rememberMe = false;
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;

    setState(() => _isLoading = true);
    await ref.read(authProvider.notifier).login(
        email: _emailController.text.trim(),
        password: _passwordController.text);
    if (!mounted) return;
    setState(() => _isLoading = false);

    final error = ref.read(authProvider).error;
    if (error != null) {
      final message = error is ApiException
          ? error.message
          : 'Login failed. Please try again.';
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message), backgroundColor: AppColors.error));
      return;
    }
    if (mounted) context.goNamed(RouteConstants.homeName);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Log In'),
      body: AuthPageLayout(
        maxWidth: 560,
        child: SingleChildScrollView(
          child: AuthSurface(
            child: Padding(
              padding: const EdgeInsets.all(28),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const AuthHeader(
                        title: 'Welcome Back',
                        subtitle: 'Log in to continue your health journey.'),
                    const SizedBox(height: 32),
                    CustomTextField(
                      controller: _emailController,
                      label: 'Email',
                      hint: 'you@example.com',
                      prefixIcon: Icons.mail_outline_rounded,
                      keyboardType: TextInputType.emailAddress,
                      validator: Validators.email,
                      textInputAction: TextInputAction.next,
                    )
                        .animate()
                        .fadeIn(duration: 300.ms, delay: 100.ms)
                        .slideY(begin: 0.1, end: 0),
                    const SizedBox(height: 16),
                    CustomTextField(
                      controller: _passwordController,
                      label: 'Password',
                      hint: 'Enter your password',
                      prefixIcon: Icons.lock_outline_rounded,
                      obscureText: true,
                      validator: Validators.password,
                      textInputAction: TextInputAction.done,
                    )
                        .animate()
                        .fadeIn(duration: 300.ms, delay: 160.ms)
                        .slideY(begin: 0.1, end: 0),
                    const SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            SizedBox(
                              width: 24,
                              height: 24,
                              child: Checkbox(
                                value: _rememberMe,
                                activeColor: AppColors.primary,
                                shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(4)),
                                onChanged: (value) => setState(
                                    () => _rememberMe = value ?? false),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text('Remember Me', style: AppTextStyles.subtext()),
                          ],
                        ),
                        TextButton(
                          onPressed: () => context
                              .goNamed(RouteConstants.forgotPasswordName),
                          child: Text('Forgot Password?',
                              style: AppTextStyles.bodyMedium(
                                  color: AppColors.primary)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 18),
                    PrimaryButton(
                            label: 'Login',
                            onPressed: _handleLogin,
                            isLoading: _isLoading)
                        .animate()
                        .fadeIn(duration: 300.ms, delay: 220.ms),
                    const SizedBox(height: 22),
                    const OrDivider(),
                    const SizedBox(height: 20),
                    const GoogleAuthButton(label: 'Continue with Google'),
                    const SizedBox(height: 26),
                    AuthFooterLink(
                      question: "Don't have an account?",
                      actionLabel: 'Register',
                      onTap: () => context.goNamed(RouteConstants.registerName),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

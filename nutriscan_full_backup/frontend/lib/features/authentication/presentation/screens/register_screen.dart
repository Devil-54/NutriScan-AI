import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/network/api_exception.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/validators.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../../../../shared/widgets/custom_select_field.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../../../profile/data/profile_model.dart';
import '../../../profile/presentation/providers/profile_provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/auth_footer_link.dart';
import '../widgets/auth_header.dart';
import '../widgets/auth_page_layout.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _confirmPassword = TextEditingController();
  final _age = TextEditingController();
  final _height = TextEditingController();
  final _weight = TextEditingController();
  final _allergies = TextEditingController();
  final _diseases = TextEditingController();
  String? _gender;
  String? _goal;
  String? _diet;
  bool? _pregnancy;
  bool? _periodStatus;
  bool _noKnownAllergies = false;
  bool _noKnownDiseases = false;
  bool _isLoading = false;

  @override
  void dispose() {
    for (final controller in [
      _name,
      _email,
      _password,
      _confirmPassword,
      _age,
      _height,
      _weight,
      _allergies,
      _diseases,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  String? _requiredChoice(String? value, String label) =>
      value == null ? 'Select $label' : null;
  String? _positiveNumber(String? value, String label) {
    final parsed = double.tryParse(value?.trim() ?? '');
    return parsed == null || parsed <= 0 ? 'Enter a valid $label' : null;
  }

  Future<void> _handleRegister() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    if (_gender == 'female' && (_pregnancy == null || _periodStatus == null)) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content:
              Text('Please complete the pregnancy and period questions.')));
      return;
    }

    final authNotifier = ref.read(authProvider.notifier);
    final profileRepo = ref.read(profileRepositoryProvider);

    setState(() => _isLoading = true);
    try {
      await authNotifier.register(
          name: _name.text.trim(),
          email: _email.text.trim(),
          password: _password.text);
      if (!mounted) return;

      await authNotifier.login(
          email: _email.text.trim(), password: _password.text);
      if (!mounted) return;

      final profile = HealthProfileModel(
        age: int.parse(_age.text.trim()),
        gender: _gender!,
        heightCm: double.parse(_height.text.trim()),
        weightKg: double.parse(_weight.text.trim()),
        bmi: 0,
        activityLevel: 'moderate',
        fitnessGoal: _goal!,
        dietPreference: _diet!,
        pregnancyStatus: _gender == 'female' ? _pregnancy : null,
        periodStatus: _gender == 'female' ? _periodStatus : null,
        allergies: _noKnownAllergies ? null : _allergies.text.trim(),
        diseases: _noKnownDiseases ? null : _diseases.text.trim(),
      );
      await profileRepo.updateProfile(profile);
      if (!mounted) return;

      context.goNamed(RouteConstants.homeName);
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text(e.message), backgroundColor: AppColors.error));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Widget _choiceField(
      {required String label,
      required String? value,
      required List<DropdownMenuItem<String>> items,
      required ValueChanged<String?> onChanged,
      required IconData icon}) {
    return CustomSelectField(
      label: label,
      value: value,
      prefixIcon: icon,
      items: items,
      onChanged: onChanged,
      validator: (v) => _requiredChoice(v, label),
      hint: 'Select $label',
    );
  }

  Widget _yesNo(String label, bool? value, ValueChanged<bool?> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.bodyMedium()),
        const SizedBox(height: 10),
        Row(
          children: [
            Expanded(
                child: ChoiceChip(
                    label: const Text('Yes'),
                    selected: value == true,
                    onSelected: (_) => onChanged(true))),
            const SizedBox(width: 12),
            Expanded(
                child: ChoiceChip(
                    label: const Text('No'),
                    selected: value == false,
                    onSelected: (_) => onChanged(false))),
          ],
        ),
        if (value == null)
          const Padding(
            padding: EdgeInsets.only(top: 6),
            child: Text('Please select an option',
                style: TextStyle(color: AppColors.error, fontSize: 12)),
          ),
      ],
    );
  }

  Widget _medicalTextField({
    required String label,
    required String hint,
    required IconData icon,
    required TextEditingController controller,
    required bool noneKnown,
    required ValueChanged<bool> onNoneKnownChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CustomTextField(
          controller: controller,
          label: label,
          hint: hint,
          prefixIcon: icon,
          enabled: !noneKnown,
          onChanged: (value) {
            if (value.trim().isNotEmpty && noneKnown) onNoneKnownChanged(false);
          },
        ),
        const SizedBox(height: 4),
        InkWell(
          borderRadius: BorderRadius.circular(8),
          onTap: () => onNoneKnownChanged(!noneKnown),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Checkbox(
                value: noneKnown,
                activeColor: AppColors.primary,
                onChanged: (value) => onNoneKnownChanged(value ?? false),
              ),
              Text('None known', style: AppTextStyles.caption()),
            ],
          ),
        ),
      ],
    );
  }

  Widget _sectionTitle(String title, String subtitle) => Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: AppTextStyles.title(color: AppColors.primary)),
            const SizedBox(height: 2),
            Text(subtitle, style: AppTextStyles.caption()),
          ],
        ),
      );

  Widget _fieldPair(BuildContext context, Widget first, Widget second) {
    final isWide = MediaQuery.sizeOf(context).width >= 600;
    if (!isWide) {
      return Column(
        children: [first, const SizedBox(height: 16), second],
      );
    }
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(child: first),
        const SizedBox(width: 16),
        Expanded(child: second),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final isFemale = _gender == 'female';
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Create Account'),
      body: AuthPageLayout(
        maxWidth: 680,
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
                          title: 'Create Your Profile',
                          subtitle:
                              'Personalized food safety starts with a few details.'),
                      const SizedBox(height: 32),
                      _sectionTitle('Personal Information',
                          'Tell us a little about yourself.'),
                      CustomTextField(
                          controller: _name,
                          label: 'Full Name',
                          hint: 'Jane Doe',
                          prefixIcon: Icons.person_outline_rounded,
                          validator: (v) =>
                              Validators.required(v, fieldName: 'Full name')),
                      const SizedBox(height: 16),
                      CustomTextField(
                          controller: _email,
                          label: 'Email',
                          hint: 'you@example.com',
                          prefixIcon: Icons.mail_outline_rounded,
                          keyboardType: TextInputType.emailAddress,
                          validator: Validators.email),
                      const SizedBox(height: 16),
                      _fieldPair(
                        context,
                        CustomTextField(
                                controller: _age,
                                label: 'Age',
                                hint: '25',
                                prefixIcon: Icons.cake_outlined,
                                keyboardType: TextInputType.number,
                                validator: (v) {
                                  final n = int.tryParse(v?.trim() ?? '');
                                  return n == null || n < 1 || n > 120
                                      ? 'Enter an age from 1 to 120'
                                      : null;
                                }),
                        _choiceField(
                                label: 'Gender',
                                value: _gender,
                                icon: Icons.person_outline_rounded,
                                onChanged: (v) => setState(() {
                                      _gender = v;
                                      _pregnancy = null;
                                      _periodStatus = null;
                                    }),
                                items: const [
                                  DropdownMenuItem(
                                      value: 'male', child: Text('Male')),
                                  DropdownMenuItem(
                                      value: 'female', child: Text('Female')),
                                  DropdownMenuItem(
                                      value: 'other', child: Text('Other')),
                                ]),
                      ),
                      const SizedBox(height: 28),
                      _sectionTitle('Account Security',
                          'Use a strong password to protect your profile.'),
                      CustomTextField(
                          controller: _password,
                          label: 'Password',
                          hint: 'At least 8 characters',
                          prefixIcon: Icons.lock_outline_rounded,
                          obscureText: true,
                          validator: Validators.password),
                      const SizedBox(height: 16),
                      CustomTextField(
                          controller: _confirmPassword,
                          label: 'Confirm Password',
                          hint: 'Re-enter your password',
                          prefixIcon: Icons.lock_outline_rounded,
                          obscureText: true,
                          validator:
                              Validators.confirmPassword(() => _password.text)),
                      if (isFemale) ...[
                        const SizedBox(height: 28),
                        _sectionTitle('Women\'s Health',
                            'Optional health context for safer recommendations.'),
                        _yesNo('Pregnancy', _pregnancy,
                            (v) => setState(() => _pregnancy = v)),
                        const SizedBox(height: 14),
                        _yesNo('Currently on Periods', _periodStatus,
                            (v) => setState(() => _periodStatus = v)),
                      ],
                      const SizedBox(height: 28),
                      _sectionTitle('Health Information',
                          'Help us tailor food insights to your goals.'),
                      _fieldPair(
                        context,
                        CustomTextField(
                                controller: _height,
                                label: 'Height (cm)',
                                hint: '170',
                                prefixIcon: Icons.height_rounded,
                                keyboardType:
                                    const TextInputType.numberWithOptions(
                                        decimal: true),
                                validator: (v) =>
                                    _positiveNumber(v, 'height')),
                        CustomTextField(
                                controller: _weight,
                                label: 'Weight (kg)',
                                hint: '65',
                                prefixIcon: Icons.monitor_weight_outlined,
                                keyboardType:
                                    const TextInputType.numberWithOptions(
                                        decimal: true),
                                validator: (v) =>
                                    _positiveNumber(v, 'weight')),
                      ),
                      const SizedBox(height: 16),
                      _fieldPair(
                        context,
                        _choiceField(
                          label: 'Diet Preference',
                          value: _diet,
                          icon: Icons.restaurant_menu_rounded,
                          onChanged: (v) => setState(() => _diet = v),
                          items: const [
                            DropdownMenuItem(
                                value: 'vegetarian', child: Text('Vegetarian')),
                            DropdownMenuItem(
                                value: 'vegan', child: Text('Vegan')),
                            DropdownMenuItem(
                                value: 'non_vegetarian',
                                child: Text('Non-vegetarian')),
                            DropdownMenuItem(
                                value: 'eggetarian', child: Text('Eggetarian')),
                            DropdownMenuItem(
                                value: 'jain', child: Text('Jain')),
                            DropdownMenuItem(
                                value: 'other', child: Text('Other'))
                          ]),
                        _choiceField(
                          label: 'Fitness Goal',
                          value: _goal,
                          icon: Icons.track_changes_rounded,
                          onChanged: (v) => setState(() => _goal = v),
                          items: const [
                            DropdownMenuItem(
                                value: 'weight_loss',
                                child: Text('Weight loss')),
                            DropdownMenuItem(
                                value: 'muscle_gain',
                                child: Text('Muscle gain')),
                            DropdownMenuItem(
                                value: 'maintenance',
                                child: Text('Maintain weight')),
                            DropdownMenuItem(
                                value: 'general_health',
                                child: Text('General health'))
                          ]),
                      ),
                      const SizedBox(height: 16),
                      _fieldPair(
                        context,
                        _medicalTextField(
                          label: 'Allergies',
                          hint: 'Enter your allergies (e.g., peanuts, milk, dust)',
                          icon: Icons.warning_amber_rounded,
                          controller: _allergies,
                          noneKnown: _noKnownAllergies,
                          onNoneKnownChanged: (value) => setState(() {
                            _noKnownAllergies = value;
                            if (value) _allergies.clear();
                          }),
                        ),
                        _medicalTextField(
                          label: 'Diseases',
                          hint:
                              'Enter your diseases/health conditions (e.g., diabetes, hypertension)',
                          icon: Icons.medical_services_outlined,
                          controller: _diseases,
                          noneKnown: _noKnownDiseases,
                          onNoneKnownChanged: (value) => setState(() {
                            _noKnownDiseases = value;
                            if (value) _diseases.clear();
                          }),
                        ),
                      ),
                      const SizedBox(height: 28),
                      PrimaryButton(
                          label: 'Create Account',
                          onPressed: _handleRegister,
                          isLoading: _isLoading),
                      const SizedBox(height: 28),
                      AuthFooterLink(
                          question: 'Already have an account?',
                          actionLabel: 'Login',
                          onTap: () =>
                              context.goNamed(RouteConstants.loginName)),
                    ]),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

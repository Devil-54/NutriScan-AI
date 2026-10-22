import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/app_error_widget.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../../../shared/widgets/health_chip.dart';
import '../../../../shared/widgets/loading_indicator.dart';
import '../../../../shared/widgets/section_header.dart';
import '../../data/profile_model.dart';
import '../../domain/profile_dummy_data.dart';
import '../providers/profile_provider.dart';
import '../widgets/editable_profile_card.dart';
import '../widgets/medical_condition_card.dart';

/// Body metrics, diet preference, and medical conditions stay editable-UI
/// only (selections update local state for visual feedback) - the backend
/// only supports editing those via id-referenced endpoints the client
/// doesn't have a catalog for yet (Phase 4F scope, unchanged from Phase 4E).
/// Fitness Goal and Activity Level map directly to HealthProfileModel
/// fields and are wired to PUT /profile/me via [healthProfileProvider].
class HealthProfileScreen extends ConsumerStatefulWidget {
  const HealthProfileScreen({super.key});

  @override
  ConsumerState<HealthProfileScreen> createState() => _HealthProfileScreenState();
}

class _HealthProfileScreenState extends ConsumerState<HealthProfileScreen> {
  final Set<String> _selectedConditions = {...dummySelectedConditions};

  /// UI label -> backend FitnessGoal enum value. The backend has no direct
  /// "weight_gain" concept on the profile itself (it's derived elsewhere
  /// from fitness_goal + activity_level), so it falls back to "maintenance".
  static const _goalToApi = {
    'Weight Loss': 'weight_loss',
    'Muscle Gain': 'muscle_gain',
    'Maintain Weight': 'maintenance',
    'Weight Gain': 'maintenance',
  };
  static const _apiToGoal = {
    'weight_loss': 'Weight Loss',
    'muscle_gain': 'Muscle Gain',
    'maintenance': 'Maintain Weight',
    'general_health': 'Maintain Weight',
  };

  String _activityToApi(String label) => label.toLowerCase().replaceAll(' ', '_');
  String _activityFromApi(String value) =>
      value.split('_').map((w) => w[0].toUpperCase() + w.substring(1)).join(' ');

  Future<void> _updateGoal(HealthProfileModel current, String uiLabel) async {
    if (current.pregnancyStatus == true && uiLabel == 'Weight Loss') return;
    final updated = HealthProfileModel(
      age: current.age,
      gender: current.gender,
      heightCm: current.heightCm,
      weightKg: current.weightKg,
      bmi: current.bmi,
      activityLevel: current.activityLevel,
      fitnessGoal: _goalToApi[uiLabel] ?? current.fitnessGoal,
      dietPreference: current.dietPreference,
      pregnancyStatus: current.pregnancyStatus,
      periodStatus: current.periodStatus,
    );
    await ref.read(healthProfileProvider.notifier).save(updated);
  }

  Future<void> _updateActivity(HealthProfileModel current, String uiLabel) async {
    final updated = HealthProfileModel(
      age: current.age,
      gender: current.gender,
      heightCm: current.heightCm,
      weightKg: current.weightKg,
      bmi: current.bmi,
      activityLevel: _activityToApi(uiLabel),
      fitnessGoal: current.fitnessGoal,
      dietPreference: current.dietPreference,
      pregnancyStatus: current.pregnancyStatus,
      periodStatus: current.periodStatus,
    );
    await ref.read(healthProfileProvider.notifier).save(updated);
  }

  @override
  Widget build(BuildContext context) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);
    final conditionColumns = ResponsiveUtils.value(context, mobile: 3, tablet: 4, desktop: 4);
    final profileAsync = ref.watch(healthProfileProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Health Profile'),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: profileAsync.when(
              loading: () => const FullScreenLoading(),
              error: (error, _) => AppErrorWidget(
                message: 'Could not load your health profile.',
                onRetry: () => ref.invalidate(healthProfileProvider),
              ),
              data: (profile) {
                final selectedGoal = profile?.pregnancyStatus == true
                    ? 'Healthy Pregnancy Weight Gain'
                    : profile != null
                        ? (_apiToGoal[profile.fitnessGoal] ?? dummySelectedFitnessGoal)
                        : dummySelectedFitnessGoal;
                final selectedActivity = profile != null ? _activityFromApi(profile.activityLevel) : dummySelectedActivityLevel;

                return ListView(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
                  children: [
                    const SectionHeader(title: 'Body Metrics'),
                    const SizedBox(height: 12),
                    GridView.count(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisCount: 2,
                      crossAxisSpacing: 10,
                      mainAxisSpacing: 10,
                      childAspectRatio: 2.6,
                      children: [
                        EditableProfileCard(label: 'Age', value: profile != null ? '${profile.age}' : dummyAge, icon: Icons.cake_outlined),
                        EditableProfileCard(label: 'Gender', value: profile?.gender ?? dummyGender, icon: Icons.wc_rounded),
                        EditableProfileCard(label: 'Height', value: profile != null ? '${profile.heightCm.toStringAsFixed(0)} cm' : dummyHeight, icon: Icons.height_rounded),
                        EditableProfileCard(label: 'Weight', value: profile != null ? '${profile.weightKg.toStringAsFixed(0)} kg' : dummyWeight, icon: Icons.monitor_weight_outlined),
                        EditableProfileCard(label: 'BMI', value: profile != null ? profile.bmi.toStringAsFixed(1) : '$dummyBmi ($dummyBmiCategory)', icon: Icons.speed_rounded),
                        const EditableProfileCard(label: 'Blood Group', value: dummyBloodGroup, icon: Icons.bloodtype_outlined),
                      ],
                    ),
                    const SizedBox(height: 28),

                    const SectionHeader(title: 'Diet Preference'),
                    const SizedBox(height: 12),
                    CustomCard(
                      child: Row(
                        children: [
                          const Icon(Icons.restaurant_menu_rounded, color: AppColors.primary),
                          const SizedBox(width: 12),
                          Text(profile?.dietPreference ?? dummyDietPreference, style: AppTextStyles.bodyMedium()),
                        ],
                      ),
                    ),
                    const SizedBox(height: 28),

                    const SectionHeader(title: 'Medical Conditions'),
                    const SizedBox(height: 12),
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: dummyMedicalConditions.length,
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: conditionColumns,
                        crossAxisSpacing: 10,
                        mainAxisSpacing: 10,
                        childAspectRatio: 0.95,
                      ),
                      itemBuilder: (context, i) {
                        final condition = dummyMedicalConditions[i];
                        final selected = _selectedConditions.contains(condition.label);
                        return MedicalConditionCard(
                          label: condition.label,
                          icon: condition.icon,
                          selected: selected,
                          onTap: () => setState(() {
                            selected ? _selectedConditions.remove(condition.label) : _selectedConditions.add(condition.label);
                          }),
                        );
                      },
                    ),
                    const SizedBox(height: 28),

                    const SectionHeader(title: 'Fitness Goal'),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 10,
                      runSpacing: 10,
                      children: [
                        for (final goal in profile?.pregnancyStatus == true
                            ? const ['Healthy Pregnancy Weight Gain']
                            : dummyFitnessGoals)
                          HealthChip(
                            label: goal,
                            selected: selectedGoal == goal,
                            onTap: profile == null || profile.pregnancyStatus == true
                                ? null
                                : () => _updateGoal(profile, goal),
                          ),
                      ],
                    ),
                    const SizedBox(height: 28),

                    const SectionHeader(title: 'Activity Level'),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 10,
                      runSpacing: 10,
                      children: [
                        for (final level in dummyActivityLevels)
                          HealthChip(
                            label: level,
                            selected: selectedActivity == level,
                            onTap: profile == null ? null : () => _updateActivity(profile, level),
                          ),
                      ],
                    ),
                    const SizedBox(height: 28),

                    const SectionHeader(title: 'Lifestyle Goals'),
                    const SizedBox(height: 12),
                    const Row(
                      children: [
                        Expanded(
                          child: EditableProfileCard(label: 'Water Intake', value: dummyWaterIntakeGoal, icon: Icons.water_drop_outlined),
                        ),
                        SizedBox(width: 10),
                        Expanded(
                          child: EditableProfileCard(label: 'Sleep Goal', value: dummySleepGoal, icon: Icons.bedtime_outlined),
                        ),
                      ],
                    ),
                  ],
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}

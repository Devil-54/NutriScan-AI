class HealthProfileModel {
  const HealthProfileModel({
    required this.age,
    required this.gender,
    required this.heightCm,
    required this.weightKg,
    required this.bmi,
    required this.activityLevel,
    required this.fitnessGoal,
    required this.dietPreference,
    this.pregnancyStatus,
    this.periodStatus,
    this.allergies,
    this.diseases,
  });

  final int age;
  final String gender;
  final double heightCm;
  final double weightKg;
  final double bmi;
  final String activityLevel;
  final String fitnessGoal;
  final String dietPreference;
  final bool? pregnancyStatus;
  final bool? periodStatus;
  final String? allergies;
  final String? diseases;

  factory HealthProfileModel.fromJson(Map<String, dynamic> json) => HealthProfileModel(
        age: json['age'] as int,
        gender: json['gender'] as String,
        heightCm: (json['height_cm'] as num).toDouble(),
        weightKg: (json['weight_kg'] as num).toDouble(),
        bmi: (json['bmi'] as num).toDouble(),
        activityLevel: json['activity_level'] as String,
        fitnessGoal: json['fitness_goal'] as String,
        dietPreference: json['diet_preference'] as String,
        pregnancyStatus: json['pregnancy_status'] as bool?,
        periodStatus: json['period_status'] as bool?,
        allergies: json['allergies'] as String?,
        diseases: json['diseases'] as String?,
      );

  Map<String, dynamic> toUpdateJson() => {
        'age': age,
        'gender': gender,
        'height_cm': heightCm.toString(),
        'weight_kg': weightKg.toString(),
        'activity_level': activityLevel,
        'fitness_goal': fitnessGoal,
        'diet_preference': dietPreference,
        'pregnancy_status': pregnancyStatus,
        'period_status': periodStatus,
        'allergies': allergies,
        'diseases': diseases,
      };
}

class FullProfileModel {
  const FullProfileModel({required this.healthProfile});
  final HealthProfileModel? healthProfile;

  factory FullProfileModel.fromJson(Map<String, dynamic> json) => FullProfileModel(
        healthProfile: json['health_profile'] != null
            ? HealthProfileModel.fromJson(json['health_profile'] as Map<String, dynamic>)
            : null,
      );
}

/// Dummy data only (Phase 4F scope) - no backend types here.
library;

class MedicalConditionOption {
  const MedicalConditionOption({required this.label, required this.icon});
  final String label;
  final String icon;
}

const dummyUserName = 'Deepak Sharma';
const dummyUserEmail = 'deepak.sharma@example.com';
const dummyMembershipStatus = 'Premium Member';

const dummyAchievements = ['7-Day Streak', 'First Scan', 'Health Explorer'];

// ---- Health Profile dummy fields ----
const dummyAge = '28';
const dummyGender = 'Male';
const dummyHeight = '175 cm';
const dummyWeight = '72 kg';
const dummyBmi = '23.5';
const dummyBmiCategory = 'Normal';
const dummyBloodGroup = 'O+';
const dummyDietPreference = 'Vegetarian';

const dummyMedicalConditions = [
  MedicalConditionOption(label: 'Diabetes', icon: '🩸'),
  MedicalConditionOption(label: 'Hypertension', icon: '❤️'),
  MedicalConditionOption(label: 'Kidney Disease', icon: '🫘'),
  MedicalConditionOption(label: 'Heart Disease', icon: '💓'),
  MedicalConditionOption(label: 'Pregnancy', icon: '🤰'),
  MedicalConditionOption(label: 'Food Allergies', icon: '🌾'),
];
const dummySelectedConditions = {'Hypertension'};

const dummyFitnessGoals = ['Weight Loss', 'Weight Gain', 'Maintain Weight', 'Muscle Gain'];
const dummySelectedFitnessGoal = 'Weight Loss';

const dummyActivityLevels = ['Sedentary', 'Light', 'Moderate', 'Active', 'Very Active'];
const dummySelectedActivityLevel = 'Moderate';

const dummyWaterIntakeGoal = '2.5 L / day';
const dummySleepGoal = '8 hrs / night';

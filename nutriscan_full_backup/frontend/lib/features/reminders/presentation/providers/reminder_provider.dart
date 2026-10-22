import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/services/storage_service.dart';
import '../../services/local_alarm_scheduler.dart';

const _storageKey = 'health_reminder_center_v1';

class MedicineReminder {
  const MedicineReminder({
    required this.id,
    required this.name,
    required this.timeMinutes,
    required this.frequency,
    required this.enabled,
  });

  final String id;
  final String name;
  final int timeMinutes;
  final int frequency;
  final bool enabled;

  MedicineReminder copyWith(
          {String? name, int? timeMinutes, int? frequency, bool? enabled}) =>
      MedicineReminder(
        id: id,
        name: name ?? this.name,
        timeMinutes: timeMinutes ?? this.timeMinutes,
        frequency: frequency ?? this.frequency,
        enabled: enabled ?? this.enabled,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'timeMinutes': timeMinutes,
        'frequency': frequency,
        'enabled': enabled,
      };

  factory MedicineReminder.fromJson(Map<String, dynamic> json) =>
      MedicineReminder(
        id: json['id'] as String,
        name: json['name'] as String,
        timeMinutes: json['timeMinutes'] as int,
        frequency: json['frequency'] as int,
        enabled: json['enabled'] as bool? ?? true,
      );
}

class ReminderState {
  const ReminderState({
    this.waterEnabled = false,
    this.waterIntervalMinutes = 60,
    this.waterStartMinutes = 8 * 60,
    this.waterEndMinutes = 22 * 60,
    this.waterGoalMl = 2500,
    this.soundEnabled = true,
    this.medicines = const [],
    this.waterCompletions = const [],
    this.medicineStatuses = const {},
  });

  final bool waterEnabled;
  final int waterIntervalMinutes;
  final int waterStartMinutes;
  final int waterEndMinutes;
  final int waterGoalMl;
  final bool soundEnabled;
  final List<MedicineReminder> medicines;

  /// Keys use yyyy-MM-dd-HH:mm so completions reset naturally each day.
  final List<String> waterCompletions;

  /// Each medicine occurrence is stored as taken or skipped by date.
  final Map<String, String> medicineStatuses;

  ReminderState copyWith({
    bool? waterEnabled,
    int? waterIntervalMinutes,
    int? waterStartMinutes,
    int? waterEndMinutes,
    int? waterGoalMl,
    bool? soundEnabled,
    List<MedicineReminder>? medicines,
    List<String>? waterCompletions,
    Map<String, String>? medicineStatuses,
  }) =>
      ReminderState(
        waterEnabled: waterEnabled ?? this.waterEnabled,
        waterIntervalMinutes: waterIntervalMinutes ?? this.waterIntervalMinutes,
        waterStartMinutes: waterStartMinutes ?? this.waterStartMinutes,
        waterEndMinutes: waterEndMinutes ?? this.waterEndMinutes,
        waterGoalMl: waterGoalMl ?? this.waterGoalMl,
        soundEnabled: soundEnabled ?? this.soundEnabled,
        medicines: medicines ?? this.medicines,
        waterCompletions: waterCompletions ?? this.waterCompletions,
        medicineStatuses: medicineStatuses ?? this.medicineStatuses,
      );

  Map<String, dynamic> toJson() => {
        'waterEnabled': waterEnabled,
        'waterIntervalMinutes': waterIntervalMinutes,
        'waterStartMinutes': waterStartMinutes,
        'waterEndMinutes': waterEndMinutes,
        'waterGoalMl': waterGoalMl,
        'soundEnabled': soundEnabled,
        'medicines': medicines.map((item) => item.toJson()).toList(),
        'waterCompletions': waterCompletions,
        'medicineStatuses': medicineStatuses,
      };

  factory ReminderState.fromJson(Map<String, dynamic> json) => ReminderState(
        waterEnabled: json['waterEnabled'] as bool? ?? false,
        waterIntervalMinutes: json['waterIntervalMinutes'] as int? ?? 60,
        waterStartMinutes: json['waterStartMinutes'] as int? ?? 480,
        waterEndMinutes: json['waterEndMinutes'] as int? ?? 1320,
        waterGoalMl: json['waterGoalMl'] as int? ?? 2500,
        soundEnabled: json['soundEnabled'] as bool? ?? true,
        medicines: ((json['medicines'] as List?) ?? const [])
            .map((item) => MedicineReminder.fromJson(
                Map<String, dynamic>.from(item as Map)))
            .toList(),
        waterCompletions:
            ((json['waterCompletions'] as List?) ?? const []).cast<String>(),
        medicineStatuses: Map<String, String>.from(
            json['medicineStatuses'] as Map? ?? const {}),
      );
}

class ReminderNotifier extends StateNotifier<ReminderState> {
  ReminderNotifier(this._storage) : super(_read(_storage)) {
    _rescheduleAlarms();
  }

  final StorageService _storage;
  final LocalAlarmScheduler _alarmScheduler = LocalAlarmScheduler();

  static ReminderState _read(StorageService storage) {
    final raw = storage.getString(_storageKey);
    if (raw == null) return const ReminderState();
    try {
      return ReminderState.fromJson(
          Map<String, dynamic>.from(jsonDecode(raw) as Map));
    } catch (_) {
      return const ReminderState();
    }
  }

  Future<void> _save(ReminderState next) async {
    state = next;
    // Start scheduling synchronously while this method is still called from the
    // picker/switch gesture, allowing browsers to show their permission prompt.
    final scheduling = _rescheduleAlarms();
    await _storage.setString(_storageKey, jsonEncode(next.toJson()));
    await scheduling;
  }

  Future<void> _rescheduleAlarms() => _alarmScheduler.reschedule([
        if (state.waterEnabled)
          for (final minute in _waterAlarmTimes(state))
            LocalReminderAlarm(
              id: 'water-$minute',
              minuteOfDay: minute,
              title: 'Water Break',
              body: 'Time to drink 250 ml of water.',
            ),
        for (final medicine in state.medicines.where((item) => item.enabled))
          for (final minute in _medicineAlarmTimes(medicine))
            LocalReminderAlarm(
              id: 'medicine-${medicine.id}-$minute',
              minuteOfDay: minute,
              title: 'Medicine Break',
              body: 'Time to take ${medicine.name}.',
            ),
      ]);

  @override
  void dispose() {
    _alarmScheduler.dispose();
    super.dispose();
  }

  Future<void> updateWater(
          {bool? enabled, int? interval, int? start, int? end, int? goalMl}) =>
      _save(
        state.copyWith(
          waterEnabled: enabled,
          waterIntervalMinutes: interval,
          waterStartMinutes: start,
          waterEndMinutes: end,
          waterGoalMl: goalMl,
        ),
      );

  Future<void> setSound(bool enabled) =>
      _save(state.copyWith(soundEnabled: enabled));

  Future<void> addMedicine(
          {required String name,
          required int timeMinutes,
          required int frequency}) =>
      _save(
        state.copyWith(
          medicines: [
            ...state.medicines,
            MedicineReminder(
              id: DateTime.now().microsecondsSinceEpoch.toString(),
              name: name,
              timeMinutes: timeMinutes,
              frequency: frequency,
              enabled: true,
            ),
          ],
        ),
      );

  Future<void> setMedicineEnabled(String id, bool enabled) =>
      _save(state.copyWith(
        medicines: state.medicines
            .map((item) =>
                item.id == id ? item.copyWith(enabled: enabled) : item)
            .toList(),
      ));

  Future<void> completeWater(String key) => _save(state.copyWith(
        waterCompletions: state.waterCompletions.contains(key)
            ? state.waterCompletions.where((item) => item != key).toList()
            : [...state.waterCompletions, key],
      ));

  Future<void> setMedicineStatus(String key, String status) {
    final next = Map<String, String>.from(state.medicineStatuses)
      ..[key] = status;
    return _save(state.copyWith(medicineStatuses: next));
  }
}

final reminderProvider =
    StateNotifierProvider<ReminderNotifier, ReminderState>((ref) {
  return ReminderNotifier(ref.watch(storageServiceProvider));
});

List<int> _waterAlarmTimes(ReminderState state) {
  final start = state.waterStartMinutes;
  final end = state.waterEndMinutes <= start
      ? state.waterEndMinutes + 24 * 60
      : state.waterEndMinutes;
  return [
    for (var minute = start + state.waterIntervalMinutes;
        minute <= end;
        minute += state.waterIntervalMinutes)
      minute % (24 * 60),
  ];
}

List<int> _medicineAlarmTimes(MedicineReminder medicine) => List.generate(
    medicine.frequency,
    (index) =>
        (medicine.timeMinutes + index * (24 * 60 ~/ medicine.frequency)) %
        (24 * 60));

import 'dart:async';

import 'browser_notification_stub.dart'
    if (dart.library.html) 'browser_notification_web.dart' as notifications;

/// A daily alarm expressed as minutes after local midnight.
class LocalReminderAlarm {
  const LocalReminderAlarm({
    required this.id,
    required this.minuteOfDay,
    required this.title,
    required this.body,
  });

  final String id;
  final int minuteOfDay;
  final String title;
  final String body;
}

/// Schedules reminders from the laptop's local wall clock.
///
/// On Flutter web [DateTime.now] is backed by JavaScript's `new Date()`;
/// this class never converts times to UTC or applies a fixed time-zone offset.
class LocalAlarmScheduler {
  Timer? _timer;
  List<LocalReminderAlarm> _alarms = const [];
  int _scheduleGeneration = 0;

  Future<void> reschedule(List<LocalReminderAlarm> alarms) async {
    final generation = ++_scheduleGeneration;
    _alarms = List.unmodifiable(alarms);
    _timer?.cancel();
    await notifications.requestNotificationPermission();
    if (generation != _scheduleGeneration) return;
    _scheduleNext();
  }

  void dispose() => _timer?.cancel();

  static DateTime? nextOccurrence(
      List<LocalReminderAlarm> alarms, DateTime now) {
    DateTime? next;
    for (final alarm in alarms) {
      final candidate = DateTime(now.year, now.month, now.day,
          alarm.minuteOfDay ~/ 60, alarm.minuteOfDay % 60);
      final occurrence = candidate.isAfter(now)
          ? candidate
          : DateTime(now.year, now.month, now.day + 1, candidate.hour,
              candidate.minute);
      if (next == null || occurrence.isBefore(next)) next = occurrence;
    }
    return next;
  }

  void _scheduleNext() {
    if (_alarms.isEmpty) return;
    final now = DateTime.now();
    LocalReminderAlarm? nextAlarm;
    DateTime? nextTime;
    for (final alarm in _alarms) {
      final candidate = DateTime(now.year, now.month, now.day,
          alarm.minuteOfDay ~/ 60, alarm.minuteOfDay % 60);
      final occurrence = candidate.isAfter(now)
          ? candidate
          : DateTime(now.year, now.month, now.day + 1, candidate.hour,
              candidate.minute);
      if (nextTime == null || occurrence.isBefore(nextTime)) {
        nextTime = occurrence;
        nextAlarm = alarm;
      }
    }
    _timer = Timer(nextTime!.difference(now), () {
      // Water and medicine can legitimately share a selected local minute.
      // Notify for every reminder due at that local clock time.
      for (final alarm in _alarms
          .where((alarm) => alarm.minuteOfDay == nextAlarm!.minuteOfDay)) {
        notifications.showReminderNotification(
            title: alarm.title, body: alarm.body);
      }
      // Re-evaluate from the current local clock so recurring/midnight alarms stay local.
      _scheduleNext();
    });
  }
}

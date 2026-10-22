import 'package:flutter_test/flutter_test.dart';
import 'package:nutriscan_app/features/reminders/services/local_alarm_scheduler.dart';

void main() {
  const alarm = LocalReminderAlarm(
    id: 'test',
    minuteOfDay: 10 * 60 + 31,
    title: 'Test',
    body: 'Test',
  );

  test('uses the local clock for an alarm one minute ahead', () {
    final now = DateTime(2026, 9, 8, 10, 30, 15);

    final scheduled = LocalAlarmScheduler.nextOccurrence([alarm], now);

    expect(scheduled, DateTime(2026, 9, 8, 10, 31));
  });

  test('moves a passed local time to the following local day', () {
    final now = DateTime(2026, 9, 8, 10, 31, 1);

    final scheduled = LocalAlarmScheduler.nextOccurrence([alarm], now);

    expect(scheduled, DateTime(2026, 9, 9, 10, 31));
  });

  test('handles AM/PM and midnight rollover without UTC conversion', () {
    const midnightAlarm = LocalReminderAlarm(
      id: 'midnight',
      minuteOfDay: 5,
      title: 'Test',
      body: 'Test',
    );
    final now = DateTime(2026, 9, 8, 23, 59, 30);

    final scheduled =
        LocalAlarmScheduler.nextOccurrence([midnightAlarm], now);

    expect(scheduled, DateTime(2026, 9, 9, 0, 5));
  });
}

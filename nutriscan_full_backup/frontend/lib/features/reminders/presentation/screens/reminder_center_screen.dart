import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../providers/reminder_provider.dart';
import '../../services/local_alarm_scheduler.dart';

class ReminderCenterScreen extends ConsumerWidget {
  const ReminderCenterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(reminderProvider);
    final now = DateTime.now();
    final waterTimes = _waterTimes(state);
    final waterDone = waterTimes
        .where(
            (minute) => state.waterCompletions.contains(_waterKey(now, minute)))
        .length;
    final medicineItems = _medicineItems(state, now);
    final medicineDone = medicineItems
        .where((item) => state.medicineStatuses[item.key] == 'taken')
        .length;
    final totalDone = waterDone + medicineDone;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Health Reminder Center'),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(
                maxWidth: ResponsiveUtils.contentMaxWidth(context)),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
              children: [
                _SummaryCard(
                  waterDone: waterDone,
                  waterTotal: waterTimes.length,
                  intakeMl: waterDone * 250,
                  goalMl: state.waterGoalMl,
                  medicineDone: medicineDone,
                  medicineTotal: medicineItems.length,
                  totalDone: totalDone,
                ),
                const SizedBox(height: 24),
                _sectionTitle('Water break reminder', '💧'),
                const SizedBox(height: 10),
                _WaterCard(state: state, times: waterTimes),
                const SizedBox(height: 24),
                _sectionTitle('Medicine reminders', '💊'),
                const SizedBox(height: 10),
                _MedicineSection(state: state, items: medicineItems),
                const SizedBox(height: 24),
                _sectionTitle('Recent reminders', '🔔'),
                const SizedBox(height: 10),
                _NotificationCenter(
                    state: state,
                    waterTimes: waterTimes,
                    medicineItems: medicineItems),
                const SizedBox(height: 24),
                _sectionTitle('Notification preferences', '⚙️'),
                const SizedBox(height: 10),
                CustomCard(
                  child: SwitchListTile.adaptive(
                    contentPadding: EdgeInsets.zero,
                    value: state.soundEnabled,
                    activeThumbColor: AppColors.primary,
                    title: Text('Notification sound',
                        style: AppTextStyles.title()),
                    subtitle: Text(
                        'Use sound for supported reminder notifications',
                        style: AppTextStyles.subtext()),
                    onChanged: (value) =>
                        ref.read(reminderProvider.notifier).setSound(value),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

Widget _sectionTitle(String title, String emoji) => Row(
      children: [
        Text(emoji, style: const TextStyle(fontSize: 18)),
        const SizedBox(width: 8),
        Text(title, style: AppTextStyles.headline()),
      ],
    );

class _SummaryCard extends StatelessWidget {
  const _SummaryCard(
      {required this.waterDone,
      required this.waterTotal,
      required this.intakeMl,
      required this.goalMl,
      required this.medicineDone,
      required this.medicineTotal,
      required this.totalDone});
  final int waterDone,
      waterTotal,
      intakeMl,
      goalMl,
      medicineDone,
      medicineTotal,
      totalDone;
  @override
  Widget build(BuildContext context) => CustomCard(
        color: AppColors.primary,
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Today\'s reminder summary',
              style: AppTextStyles.headline(color: Colors.white)),
          const SizedBox(height: 12),
          Text('Water progress: $waterDone/$waterTotal reminders completed',
              style: AppTextStyles.subtext(
                  color: Colors.white.withValues(alpha: .9))),
          Text('Water intake: ${_litres(intakeMl)} L / ${_litres(goalMl)} L',
              style: AppTextStyles.subtext(
                  color: Colors.white.withValues(alpha: .9))),
          Text('Medicine: $medicineDone/$medicineTotal completed',
              style: AppTextStyles.subtext(
                  color: Colors.white.withValues(alpha: .9))),
          const SizedBox(height: 8),
          Text('$totalDone total reminders completed today',
              style: AppTextStyles.title(color: Colors.white)),
        ]),
      );
}

class _WaterCard extends ConsumerWidget {
  const _WaterCard({required this.state, required this.times});
  final ReminderState state;
  final List<int> times;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifier = ref.read(reminderProvider.notifier);
    final now = DateTime.now();
    final next = _nextOccurrence(times, now);
    return CustomCard(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      SwitchListTile.adaptive(
          contentPadding: EdgeInsets.zero,
          value: state.waterEnabled,
          activeThumbColor: AppColors.primary,
          title: Text('Water reminders', style: AppTextStyles.title()),
          subtitle: Text(
              state.waterEnabled ? 'Time to drink water.' : 'Currently paused',
              style: AppTextStyles.subtext()),
          onChanged: (value) => notifier.updateWater(enabled: value)),
      const Divider(),
      Wrap(spacing: 8, runSpacing: 8, children: [
        _SelectChip(
            label: _timeLabel(state.waterStartMinutes),
            icon: Icons.wb_sunny_outlined,
            onTap: () => _pickTime(context, state.waterStartMinutes,
                (value) => notifier.updateWater(start: value))),
        _SelectChip(
            label: _timeLabel(state.waterEndMinutes),
            icon: Icons.nights_stay_outlined,
            onTap: () => _pickTime(context, state.waterEndMinutes,
                (value) => notifier.updateWater(end: value))),
        _IntervalMenu(
            value: state.waterIntervalMinutes,
            onChanged: (value) => notifier.updateWater(interval: value)),
        _GoalMenu(
            value: state.waterGoalMl,
            onChanged: (value) => notifier.updateWater(goalMl: value)),
      ]),
      const SizedBox(height: 14),
      Text(
          next == null
              ? 'No reminder scheduled'
              : 'Next reminder: ${_timeLabel(next.hour * 60 + next.minute)}',
          style: AppTextStyles.bodyMedium(color: AppColors.primary)),
      const SizedBox(height: 6),
      Text('Suggested schedule: ${times.map(_timeLabel).join(' • ')}',
          style: AppTextStyles.caption()),
      if (state.waterEnabled && times.isNotEmpty) ...[
        const SizedBox(height: 14),
        OutlinedButton.icon(
            onPressed: () => notifier.completeWater(_waterKey(
                now,
                times.firstWhere(
                    (minute) => minute <= now.hour * 60 + now.minute,
                    orElse: () => times.first))),
            icon: const Icon(Icons.water_drop_outlined),
            label: const Text('Drink 250 ml / Completed')),
      ],
    ]));
  }
}

class _MedicineSection extends ConsumerWidget {
  const _MedicineSection({required this.state, required this.items});
  final ReminderState state;
  final List<_MedicineItem> items;
  @override
  Widget build(BuildContext context, WidgetRef ref) => Column(children: [
        for (final medicine in state.medicines) ...[
          CustomCard(
              child: SwitchListTile.adaptive(
                  contentPadding: EdgeInsets.zero,
                  value: medicine.enabled,
                  activeThumbColor: AppColors.primary,
                  title: Text(medicine.name, style: AppTextStyles.title()),
                  subtitle: Text(
                      '${_frequencyLabel(medicine.frequency)} • ${_medicineTimes(medicine).map(_timeLabel).join(', ')}',
                      style: AppTextStyles.subtext()),
                  onChanged: (value) => ref
                      .read(reminderProvider.notifier)
                      .setMedicineEnabled(medicine.id, value))),
          const SizedBox(height: 10),
        ],
        if (state.medicines.isEmpty)
          CustomCard(
              child: Text(
                  'No medicines added. This is only a personal reminder tool.',
                  style: AppTextStyles.subtext())),
        const SizedBox(height: 10),
        Align(
            alignment: Alignment.centerLeft,
            child: OutlinedButton.icon(
                icon: const Icon(Icons.add),
                label: const Text('Add medicine reminder'),
                onPressed: () => _showAddMedicine(context, ref))),
        if (items.isNotEmpty) ...[
          const SizedBox(height: 10),
          ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: _MedicineStatusItem(item: item, state: state))),
        ],
      ]);
}

class _MedicineStatusItem extends ConsumerWidget {
  const _MedicineStatusItem({required this.item, required this.state});
  final _MedicineItem item;
  final ReminderState state;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = state.medicineStatuses[item.key];
    return CustomCard(
        padding: const EdgeInsets.all(12),
        child: Row(children: [
          const Icon(Icons.medication_outlined, color: AppColors.primary),
          const SizedBox(width: 10),
          Expanded(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Text(item.medicine.name, style: AppTextStyles.bodyMedium()),
                Text(
                    '${_timeLabel(item.time)} • ${status == null ? 'Pending' : status == 'taken' ? 'Taken' : 'Skipped'}',
                    style: AppTextStyles.caption(
                        color: status == 'taken'
                            ? AppColors.success
                            : status == 'skipped'
                                ? AppColors.warning
                                : AppColors.subtext))
              ])),
          if (status == null) ...[
            TextButton(
                onPressed: () => ref
                    .read(reminderProvider.notifier)
                    .setMedicineStatus(item.key, 'taken'),
                child: const Text('Taken')),
            TextButton(
                onPressed: () => ref
                    .read(reminderProvider.notifier)
                    .setMedicineStatus(item.key, 'skipped'),
                child: const Text('Skip')),
          ],
        ]));
  }
}

class _NotificationCenter extends StatelessWidget {
  const _NotificationCenter(
      {required this.state,
      required this.waterTimes,
      required this.medicineItems});
  final ReminderState state;
  final List<int> waterTimes;
  final List<_MedicineItem> medicineItems;
  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final waterNext = _nextOccurrence(waterTimes, now);
    return CustomCard(
        child: Column(children: [
      _Notice(
          icon: Icons.water_drop_outlined,
          title: 'Water Reminder',
          detail: waterNext == null
              ? 'No reminder scheduled'
              : 'Drink 250 ml • Next reminder: ${_timeLabel(waterNext.hour * 60 + waterNext.minute)}',
          status: state.waterEnabled ? 'Active' : 'Paused'),
      if (medicineItems.isNotEmpty) const Divider(height: 22),
      for (var i = 0; i < medicineItems.length; i++) ...[
        _Notice(
            icon: Icons.medication_outlined,
            title: 'Medicine Reminder',
            detail:
                'Medicine: ${medicineItems[i].medicine.name} • ${_timeLabel(medicineItems[i].time)}',
            status: _statusLabel(state.medicineStatuses[medicineItems[i].key])),
        if (i != medicineItems.length - 1) const Divider(height: 22),
      ],
    ]));
  }
}

class _Notice extends StatelessWidget {
  const _Notice(
      {required this.icon,
      required this.title,
      required this.detail,
      required this.status});
  final IconData icon;
  final String title, detail, status;
  @override
  Widget build(BuildContext context) =>
      Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(icon, color: AppColors.primary),
        const SizedBox(width: 10),
        Expanded(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: AppTextStyles.bodyMedium()),
          Text(detail, style: AppTextStyles.caption()),
          Text(status,
              style: AppTextStyles.caption(
                  color: status == 'Taken'
                      ? AppColors.success
                      : AppColors.subtext))
        ]))
      ]);
}

class _SelectChip extends StatelessWidget {
  const _SelectChip(
      {required this.label, required this.icon, required this.onTap});
  final String label;
  final IconData icon;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => ActionChip(
      avatar: Icon(icon, size: 16), label: Text(label), onPressed: onTap);
}

class _IntervalMenu extends StatelessWidget {
  const _IntervalMenu({required this.value, required this.onChanged});
  final int value;
  final ValueChanged<int> onChanged;
  @override
  Widget build(BuildContext context) => PopupMenuButton<int>(
      onSelected: onChanged,
      itemBuilder: (_) => const [
            PopupMenuItem(value: 30, child: Text('Every 30 minutes')),
            PopupMenuItem(value: 60, child: Text('Every 1 hour')),
            PopupMenuItem(value: 120, child: Text('Every 2 hours'))
          ],
      child: Chip(
          avatar: const Icon(Icons.timer_outlined, size: 16),
          label: Text('Every ${value < 60 ? '30 min' : '${value ~/ 60} hr'}')));
}

class _GoalMenu extends StatelessWidget {
  const _GoalMenu({required this.value, required this.onChanged});
  final int value;
  final ValueChanged<int> onChanged;
  @override
  Widget build(BuildContext context) => PopupMenuButton<int>(
      onSelected: onChanged,
      itemBuilder: (_) => const [
            PopupMenuItem(value: 1500, child: Text('1.5 L goal')),
            PopupMenuItem(value: 2000, child: Text('2.0 L goal')),
            PopupMenuItem(value: 2500, child: Text('2.5 L goal')),
            PopupMenuItem(value: 3000, child: Text('3.0 L goal'))
          ],
      child: Chip(
          avatar: const Icon(Icons.flag_outlined, size: 16),
          label: Text('${_litres(value)} L goal')));
}

Future<void> _pickTime(
    BuildContext context, int current, ValueChanged<int> onPicked) async {
  final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay(hour: current ~/ 60, minute: current % 60));
  if (time != null) onPicked(time.hour * 60 + time.minute);
}

Future<void> _showAddMedicine(BuildContext context, WidgetRef ref) async {
  final controller = TextEditingController();
  var time = const TimeOfDay(hour: 8, minute: 0);
  var frequency = 1;
  await showDialog<void>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
          builder: (context, setState) => AlertDialog(
                  title: const Text('Add medicine reminder'),
                  content: Column(mainAxisSize: MainAxisSize.min, children: [
                    TextField(
                        controller: controller,
                        autofocus: true,
                        decoration:
                            const InputDecoration(labelText: 'Medicine name')),
                    const SizedBox(height: 12),
                    ListTile(
                        contentPadding: EdgeInsets.zero,
                        title: const Text('Reminder time'),
                        trailing: Text(time.format(context)),
                        onTap: () async {
                          final picked = await showTimePicker(
                              context: context, initialTime: time);
                          if (picked != null) setState(() => time = picked);
                        }),
                    DropdownButtonFormField<int>(
                        initialValue: frequency,
                        decoration:
                            const InputDecoration(labelText: 'Frequency'),
                        items: const [
                          DropdownMenuItem(value: 1, child: Text('Once a day')),
                          DropdownMenuItem(
                              value: 2, child: Text('Twice a day')),
                          DropdownMenuItem(
                              value: 3, child: Text('Three times a day'))
                        ],
                        onChanged: (value) =>
                            setState(() => frequency = value ?? 1))
                  ]),
                  actions: [
                    TextButton(
                        onPressed: () => Navigator.pop(dialogContext),
                        child: const Text('Cancel')),
                    FilledButton(
                        onPressed: () {
                          final name = controller.text.trim();
                          if (name.isEmpty) return;
                          ref.read(reminderProvider.notifier).addMedicine(
                              name: name,
                              timeMinutes: time.hour * 60 + time.minute,
                              frequency: frequency);
                          Navigator.pop(dialogContext);
                        },
                        child: const Text('Add'))
                  ])));
  controller.dispose();
}

List<int> _waterTimes(ReminderState state) {
  final end = state.waterEndMinutes <= state.waterStartMinutes
      ? state.waterEndMinutes + 24 * 60
      : state.waterEndMinutes;
  final times = <int>[];
  for (var time = state.waterStartMinutes + state.waterIntervalMinutes;
      time <= end;
      time += state.waterIntervalMinutes) {
    times.add(time % (24 * 60));
  }
  return times;
}

DateTime? _nextOccurrence(List<int> times, DateTime now) =>
    LocalAlarmScheduler.nextOccurrence(
      [
        for (final minute in times)
          LocalReminderAlarm(
              id: 'display-$minute',
              minuteOfDay: minute,
              title: '',
              body: ''),
      ],
      now,
    );

List<int> _medicineTimes(MedicineReminder medicine) => List.generate(
    medicine.frequency,
    (index) =>
        (medicine.timeMinutes + index * (24 * 60 ~/ medicine.frequency)) %
        (24 * 60));
List<_MedicineItem> _medicineItems(ReminderState state, DateTime day) => [
      for (final medicine
          in state.medicines.where((medicine) => medicine.enabled))
        for (final time in _medicineTimes(medicine))
          _MedicineItem(medicine, time, '${medicine.id}-${_dayKey(day)}-$time')
    ];

class _MedicineItem {
  const _MedicineItem(this.medicine, this.time, this.key);
  final MedicineReminder medicine;
  final int time;
  final String key;
}

String _dayKey(DateTime date) =>
    '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
String _waterKey(DateTime date, int minute) =>
    '${_dayKey(date)}-${minute ~/ 60}-${minute % 60}';
String _timeLabel(int minutes) {
  final hour = minutes ~/ 60;
  final minute = minutes % 60;
  final suffix = hour >= 12 ? 'PM' : 'AM';
  final displayHour = hour % 12 == 0 ? 12 : hour % 12;
  return '$displayHour:${minute.toString().padLeft(2, '0')} $suffix';
}

String _frequencyLabel(int frequency) => switch (frequency) {
      1 => 'Once a day',
      2 => 'Twice a day',
      _ => 'Three times a day'
    };
String _statusLabel(String? status) => status == 'taken'
    ? 'Taken'
    : status == 'skipped'
        ? 'Skipped'
        : 'Pending';
String _litres(int ml) => (ml / 1000).toStringAsFixed(ml % 1000 == 0 ? 0 : 1);

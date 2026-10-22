import 'dart:js_interop';

import 'package:web/web.dart' as web;

Future<void> requestNotificationPermission() async {
  if (web.Notification.permission == 'default') {
    await web.Notification.requestPermission().toDart;
  }
}

void showReminderNotification({required String title, required String body}) {
  if (web.Notification.permission == 'granted') {
    web.Notification(title, web.NotificationOptions(body: body));
  }
}

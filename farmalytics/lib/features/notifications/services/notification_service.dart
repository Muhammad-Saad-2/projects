import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;
import 'package:flutter/material.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notifications = FlutterLocalNotificationsPlugin();

  Future<void> init() async {
    tz.initializeTimeZones();
    
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
    );

    await _notifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (details) {
        // Handle notification tap
      },
    );

    // Request permissions for Android 13+
    await _notifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();
  }

  Future<void> scheduleWateringReminder({
    required int id,
    required String cropName,
    required TimeOfDay time,
    required DateTime startDate,
    List<dynamic>? forecast, // Pass forecast data for smart logic
  }) async {
    final now = DateTime.now();
    
    // We'll schedule for the next 7 days based on the frequency
    // For simplicity, let's just schedule tomorrow's check
    var scheduledDate = DateTime(
      now.year,
      now.month,
      now.day,
      time.hour,
      time.minute,
    );

    if (scheduledDate.isBefore(now)) {
      scheduledDate = scheduledDate.add(const Duration(days: 1));
    }

    String title = 'Time to water: $cropName 🌿';
    String body = 'Your scheduled watering for $cropName starts now.';

    // Smart logic: Check forecast for the scheduled date
    if (forecast != null && forecast.isNotEmpty) {
      final dateStr = '${scheduledDate.year}-${scheduledDate.month.toString().padLeft(2, '0')}-${scheduledDate.day.toString().padLeft(2, '0')}';
      
      // Try to find the forecast for this date
      final dayForecast = forecast.firstWhere(
        (day) => day.date == dateStr,
        orElse: () => null,
      );

      if (dayForecast != null && dayForecast.condition.toLowerCase().contains('rain')) {
        title = 'Rainy Day Alert! 🌧️';
        body = 'Rain is predicted for $cropName today. Consider skipping your scheduled watering.';
      }
    }

    await _notifications.zonedSchedule(
      id,
      title,
      body,
      tz.TZDateTime.from(scheduledDate, tz.local),
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'watering_channel',
          'Watering Reminders',
          channelDescription: 'Smart alerts to water your crops',
          importance: Importance.max,
          priority: Priority.high,
          styleInformation: BigTextStyleInformation(''),
        ),
      ),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      // For daily repeats we could use matchDateTimeComponents: DateTimeComponents.time
      // But for "Smart" logic we want to check weather again or schedule specific instances
    );
  }

  Future<void> cancelNotification(int id) async {
    await _notifications.cancel(id);
  }
}

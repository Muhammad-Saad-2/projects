import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/watering_service.dart';
import '../models/watering_model.dart';
import '../../notifications/services/notification_service.dart';
import 'add_watering_screen.dart';

class WateringListScreen extends StatelessWidget {
  const WateringListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = context.watch<User?>();
    final wateringService = WateringService();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Watering Schedule'),
        backgroundColor: Colors.cyan.shade700,
        foregroundColor: Colors.white,
      ),
      body: user == null
          ? const Center(child: Text('Please login to view schedules'))
          : StreamBuilder<List<WateringSchedule>>(
              stream: wateringService.getSchedules(user.uid),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return Center(child: Text('Error: ${snapshot.error}'));
                }

                final schedules = snapshot.data ?? [];
                if (schedules.isEmpty) {
                  return _buildEmptyState();
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: schedules.length,
                  itemBuilder: (context, index) {
                    final schedule = schedules[index];
                    return _buildScheduleCard(context, schedule);
                  },
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AddWateringScreen()),
          );
        },
        backgroundColor: Colors.cyan.shade700,
        foregroundColor: Colors.white,
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.water_drop_outlined, size: 64, color: Colors.cyan.shade200),
          const SizedBox(height: 16),
          const Text(
            'No watering schedules set yet.\nAdd one to keep your crops hydrated!',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildScheduleCard(BuildContext context, WateringSchedule schedule) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ListTile(
        leading: const CircleAvatar(
          backgroundColor: Colors.cyan,
          child: Icon(Icons.water_drop, color: Colors.white),
        ),
        title: Text(
          schedule.cropName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          '${schedule.frequency.name.toUpperCase()} at ${schedule.startTime.format(context)}',
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline, color: Colors.red),
          onPressed: () {
            WateringService().deleteSchedule(schedule.id);
            NotificationService().cancelNotification(schedule.id.hashCode);
          },
        ),
      ),
    );
  }
}

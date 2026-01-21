import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../crops/models/crop_model.dart';
import '../../crops/services/crop_service.dart';
import '../../weather/weather_service.dart';
import '../../notifications/services/notification_service.dart';
import '../models/watering_model.dart';
import '../services/watering_service.dart';

class AddWateringScreen extends StatefulWidget {
  const AddWateringScreen({super.key});

  @override
  State<AddWateringScreen> createState() => _AddWateringScreenState();
}

class _AddWateringScreenState extends State<AddWateringScreen> {
  Crop? _selectedCrop;
  WateringFrequency _frequency = WateringFrequency.daily;
  TimeOfDay _startTime = const TimeOfDay(hour: 8, minute: 0);
  bool _isLoading = false;

  Future<void> _selectTime() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _startTime,
    );
    if (picked != null) setState(() => _startTime = picked);
  }

  Future<void> _save() async {
    if (_selectedCrop == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a crop')),
      );
      return;
    }

    final user = context.read<User?>();
    if (user == null) return;

    setState(() => _isLoading = true);
    try {
      final weatherService = WeatherService();
      final weatherData = await weatherService.fetchWeather();

      final schedule = WateringSchedule(
        id: '', // Will be set by Firestore
        userId: user.uid,
        cropId: _selectedCrop!.id,
        cropName: _selectedCrop!.name,
        frequency: _frequency,
        startTime: _startTime,
        startDate: DateTime.now(),
      );

      final docRef = await WateringService().addSchedule(schedule);
      
      // Schedule local notification
      final notificationService = NotificationService();
      await notificationService.scheduleWateringReminder(
        id: docRef.id.hashCode, // Unique int ID for local notifications
        cropName: _selectedCrop!.name,
        time: _startTime,
        startDate: DateTime.now(),
        forecast: weatherData.forecast,
      );

      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to save: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = context.watch<User?>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('New Watering Plan'),
        backgroundColor: Colors.cyan.shade700,
        foregroundColor: Colors.white,
      ),
      body: user == null
          ? const Center(child: Text('Login required'))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _buildCropSelector(user.uid),
                  const SizedBox(height: 24),
                  _buildFrequencySelector(),
                  const SizedBox(height: 24),
                  _buildTimeSelector(),
                  const SizedBox(height: 40),
                  ElevatedButton(
                    onPressed: _isLoading ? null : _save,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.cyan.shade700,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.all(16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('Save Schedule', style: TextStyle(fontSize: 18)),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildCropSelector(String userId) {
    return StreamBuilder<List<Crop>>(
      stream: CropService().getActiveCrops(userId),
      builder: (context, snapshot) {
        final crops = snapshot.data ?? [];
        return DropdownButtonFormField<Crop>(
          value: _selectedCrop,
          decoration: const InputDecoration(
            labelText: 'Select Crop',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.eco),
          ),
          items: crops.map((crop) {
            return DropdownMenuItem(value: crop, child: Text(crop.name));
          }).toList(),
          onChanged: (val) => setState(() => _selectedCrop = val),
        );
      },
    );
  }

  Widget _buildFrequencySelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Frequency', style: TextStyle(color: Colors.grey)),
        const SizedBox(height: 8),
        SegmentedButton<WateringFrequency>(
          segments: const [
            ButtonSegment(value: WateringFrequency.daily, label: Text('Daily')),
            ButtonSegment(value: WateringFrequency.alternate, label: Text('Alternate')),
            ButtonSegment(value: WateringFrequency.custom, label: Text('Custom')),
          ],
          selected: {_frequency},
          onSelectionChanged: (set) => setState(() => _frequency = set.first),
        ),
      ],
    );
  }

  Widget _buildTimeSelector() {
    return ListTile(
      title: const Text('Start Time'),
      subtitle: Text(_startTime.format(context)),
      trailing: const Icon(Icons.access_time),
      shape: RoundedRectangleBorder(
        side: const BorderSide(color: Colors.grey),
        borderRadius: BorderRadius.circular(4),
      ),
      onTap: _selectTime,
    );
  }
}

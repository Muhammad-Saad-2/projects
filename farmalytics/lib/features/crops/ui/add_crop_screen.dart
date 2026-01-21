import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:farmalytics/features/crops/models/crop_model.dart';
import 'package:farmalytics/features/crops/services/crop_service.dart';

class AddCropScreen extends StatefulWidget {
  const AddCropScreen({super.key});

  @override
  State<AddCropScreen> createState() => _AddCropScreenState();
}

class _AddCropScreenState extends State<AddCropScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _fieldController = TextEditingController();
  DateTime _sowingDate = DateTime.now();
  DateTime? _expectedHarvestDate;
  CropStage _selectedStage = CropStage.seedling;
  bool _isLoading = false;

  Future<void> _selectSowingDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _sowingDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null) setState(() => _sowingDate = picked);
  }

  Future<void> _selectHarvestDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _expectedHarvestDate ?? DateTime.now().add(const Duration(days: 90)),
      firstDate: _sowingDate,
      lastDate: _sowingDate.add(const Duration(days: 730)),
    );
    if (picked != null) setState(() => _expectedHarvestDate = picked);
  }

  Future<void> _saveCrop() async {
    if (!_formKey.currentState!.validate()) return;

    final user = context.read<User?>();
    if (user == null) return;

    setState(() => _isLoading = true);

    try {
      final cropService = CropService();
      final newCrop = Crop(
        id: '', // Firestore will generate
        userId: user.uid,
        name: _nameController.text.trim(),
        fieldName: _fieldController.text.trim().isEmpty ? null : _fieldController.text.trim(),
        sowingDate: _sowingDate,
        expectedHarvestDate: _expectedHarvestDate,
        stage: _selectedStage,
      );

      await cropService.addCrop(newCrop);
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to add crop: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add New Crop'),
        backgroundColor: const Color(0xFF2E7D32),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Crop Name',
                  hintText: 'e.g. Tomato, Wheat',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.eco),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Please enter crop name';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _fieldController,
                decoration: const InputDecoration(
                  labelText: 'Field / Plot Name (Optional)',
                  hintText: 'e.g. North Plot, Plot A',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.map),
                ),
              ),
              const SizedBox(height: 24),
              ListTile(
                title: const Text('Sowing Date'),
                subtitle: Text(DateFormat('MMM dd, yyyy').format(_sowingDate)),
                trailing: const Icon(Icons.calendar_today),
                shape: RoundedRectangleBorder(
                  side: const BorderSide(color: Colors.grey),
                  borderRadius: BorderRadius.circular(4),
                ),
                onTap: _selectSowingDate,
              ),
              const SizedBox(height: 16),
              ListTile(
                title: const Text('Expected Harvest Date'),
                subtitle: Text(_expectedHarvestDate != null
                    ? DateFormat('MMM dd, yyyy').format(_expectedHarvestDate!)
                    : 'Not set'),
                trailing: const Icon(Icons.event_available),
                shape: RoundedRectangleBorder(
                  side: const BorderSide(color: Colors.grey),
                  borderRadius: BorderRadius.circular(4),
                ),
                onTap: _selectHarvestDate,
              ),
              const SizedBox(height: 24),
              DropdownButtonFormField<CropStage>(
                value: _selectedStage,
                decoration: const InputDecoration(
                  labelText: 'Current Stage',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.trending_up),
                ),
                items: CropStage.values.map((stage) {
                  return DropdownMenuItem(
                    value: stage,
                    child: Text(stage.displayName),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _selectedStage = value);
                  }
                },
              ),
              const SizedBox(height: 48),
              ElevatedButton(
                onPressed: _isLoading ? null : _saveCrop,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2E7D32),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('Add Crop', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

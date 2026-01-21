import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../crops/models/crop_model.dart';
import '../../crops/services/crop_service.dart';
import '../models/treatment_model.dart';
import '../services/treatment_service.dart';

class AddTreatmentScreen extends StatefulWidget {
  const AddTreatmentScreen({super.key});

  @override
  State<AddTreatmentScreen> createState() => _AddTreatmentScreenState();
}

class _AddTreatmentScreenState extends State<AddTreatmentScreen> {
  final _formKey = GlobalKey<FormState>();
  final _productController = TextEditingController();
  final _quantityController = TextEditingController();
  final _unitController = TextEditingController(text: 'kg');
  
  Crop? _selectedCrop;
  TreatmentType _selectedType = TreatmentType.fertilizer;
  DateTime _appliedDate = DateTime.now();
  bool _isLoading = false;

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _appliedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) setState(() => _appliedDate = picked);
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate() || _selectedCrop == null) {
      if (_selectedCrop == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please select a crop')),
        );
      }
      return;
    }

    final user = context.read<User?>();
    if (user == null) return;

    setState(() => _isLoading = true);
    try {
      final treatment = Treatment(
        id: '',
        userId: user.uid,
        cropId: _selectedCrop!.id,
        cropName: _selectedCrop!.name,
        type: _selectedType,
        productName: _productController.text.trim(),
        quantity: double.parse(_quantityController.text),
        unit: _unitController.text.trim(),
        appliedDate: _appliedDate,
      );

      await TreatmentService().addTreatment(treatment);
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
        title: const Text('Add Treatment'),
        backgroundColor: Colors.orange.shade800,
        foregroundColor: Colors.white,
      ),
      body: user == null
          ? const Center(child: Text('Login required'))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _buildCropSelector(user.uid),
                    const SizedBox(height: 24),
                    _buildTypeSelector(),
                    const SizedBox(height: 24),
                    TextFormField(
                      controller: _productController,
                      decoration: const InputDecoration(
                        labelText: 'Product Name',
                        hintText: 'e.g. Urea, Neem Oil',
                        border: OutlineInputBorder(),
                      ),
                      validator: (val) => val?.isEmpty ?? true ? 'Required' : null,
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          flex: 2,
                          child: TextFormField(
                            controller: _quantityController,
                            decoration: const InputDecoration(
                              labelText: 'Quantity',
                              border: OutlineInputBorder(),
                            ),
                            keyboardType: TextInputType.number,
                            validator: (val) => double.tryParse(val ?? '') == null ? 'Invalid' : null,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: TextFormField(
                            controller: _unitController,
                            decoration: const InputDecoration(
                              labelText: 'Unit',
                              border: OutlineInputBorder(),
                            ),
                            validator: (val) => val?.isEmpty ?? true ? 'Required' : null,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    ListTile(
                      title: const Text('Date Applied'),
                      subtitle: Text(DateFormat('MMM dd, yyyy').format(_appliedDate)),
                      trailing: const Icon(Icons.calendar_today),
                      shape: RoundedRectangleBorder(
                        side: const BorderSide(color: Colors.grey),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      onTap: _selectDate,
                    ),
                    const SizedBox(height: 40),
                    ElevatedButton(
                      onPressed: _isLoading ? null : _save,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange.shade800,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.all(16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: _isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('Add Record', style: TextStyle(fontSize: 18)),
                    ),
                  ],
                ),
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

  Widget _buildTypeSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Treatment Type', style: TextStyle(color: Colors.grey)),
        const SizedBox(height: 8),
        SegmentedButton<TreatmentType>(
          segments: const [
            ButtonSegment(value: TreatmentType.fertilizer, label: Text('Fertilizer')),
            ButtonSegment(value: TreatmentType.pesticide, label: Text('Pesticide')),
          ],
          selected: {_selectedType},
          onSelectionChanged: (set) => setState(() => _selectedType = set.first),
        ),
      ],
    );
  }
}

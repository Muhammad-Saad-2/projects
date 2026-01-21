import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/crop_model.dart';
import '../services/crop_service.dart';

class CropDetailScreen extends StatefulWidget {
  final Crop crop;
  const CropDetailScreen({super.key, required this.crop});

  @override
  State<CropDetailScreen> createState() => _CropDetailScreenState();
}

class _CropDetailScreenState extends State<CropDetailScreen> {
  late Crop _currentCrop;
  bool _isUpdating = false;

  @override
  void initState() {
    super.initState();
    _currentCrop = widget.crop;
  }

  Future<void> _updateStage(CropStage? newStage) async {
    if (newStage == null || newStage == _currentCrop.stage) return;

    setState(() => _isUpdating = true);
    try {
      await CropService().updateCropStage(_currentCrop.id, newStage);
      setState(() {
        _currentCrop = _currentCrop.copyWith(stage: newStage);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Stage updated successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Update failed: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isUpdating = false);
    }
  }

  Future<void> _harvestCrop() async {
    setState(() => _isUpdating = true);
    try {
      await CropService().archiveCrop(_currentCrop.id);
      setState(() {
        _currentCrop = _currentCrop.copyWith(
          isArchived: true,
          stage: CropStage.harvest,
        );
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Crop marked as harvested')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Action failed: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isUpdating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_currentCrop.name),
        backgroundColor: const Color(0xFF2E7D32),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoCard(),
            const SizedBox(height: 32),
            const Text(
              'Actions',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildStageSelector(),
            const SizedBox(height: 16),
            if (!_currentCrop.isArchived)
              ElevatedButton.icon(
                onPressed: _isUpdating ? null : _harvestCrop,
                icon: const Icon(Icons.check_circle),
                label: const Text('Mark as Harvested'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.green.shade100),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            _InfoRow(label: 'Field / Plot', value: _currentCrop.fieldName ?? 'Default Plot'),
            const Divider(),
            _InfoRow(label: 'Sowing Date', value: DateFormat('MMM dd, yyyy').format(_currentCrop.sowingDate)),
            const Divider(),
            _InfoRow(
              label: 'Expected Harvest',
              value: _currentCrop.expectedHarvestDate != null
                  ? DateFormat('MMM dd, yyyy').format(_currentCrop.expectedHarvestDate!)
                  : 'TBD',
            ),
            const Divider(),
            _InfoRow(
              label: 'Status',
              value: _currentCrop.isArchived ? 'Harvested' : 'Active',
              valueColor: _currentCrop.isArchived ? Colors.orange : Colors.green,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStageSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Update Growth Stage', style: TextStyle(color: Colors.grey)),
        const SizedBox(height: 8),
        DropdownButtonFormField<CropStage>(
          value: _currentCrop.stage,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            contentPadding: EdgeInsets.symmetric(horizontal: 16),
          ),
          items: CropStage.values.map((stage) {
            return DropdownMenuItem(
              value: stage,
              child: Text(stage.displayName),
            );
          }).toList(),
          onChanged: _isUpdating ? null : _updateStage,
        ),
      ],
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;

  const _InfoRow({required this.label, required this.value, this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: valueColor ?? Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}

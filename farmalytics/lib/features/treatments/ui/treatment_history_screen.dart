import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/treatment_service.dart';
import '../models/treatment_model.dart';
import 'add_treatment_screen.dart';

class TreatmentHistoryScreen extends StatelessWidget {
  const TreatmentHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = context.watch<User?>();
    final treatmentService = TreatmentService();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Fertilizer & Pesticide'),
        backgroundColor: Colors.orange.shade800,
        foregroundColor: Colors.white,
      ),
      body: user == null
          ? const Center(child: Text('Please login'))
          : StreamBuilder<List<Treatment>>(
              stream: treatmentService.getTreatments(user.uid),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return Center(child: Text('Error: ${snapshot.error}'));
                }

                final treatments = snapshot.data ?? [];
                if (treatments.isEmpty) {
                  return _buildEmptyState();
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: treatments.length,
                  itemBuilder: (context, index) {
                    final treatment = treatments[index];
                    return _buildTreatmentCard(context, treatment);
                  },
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AddTreatmentScreen()),
          );
        },
        backgroundColor: Colors.orange.shade800,
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
          Icon(Icons.science_outlined, size: 64, color: Colors.orange.shade200),
          const SizedBox(height: 16),
          const Text(
            'No treatments logged yet.\nKeep track of your crop care here.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildTreatmentCard(BuildContext context, Treatment treatment) {
    final bool isFertilizer = treatment.type == TreatmentType.fertilizer;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: isFertilizer ? Colors.green.shade100 : Colors.orange.shade100,
          child: Icon(
            isFertilizer ? Icons.grass : Icons.bug_report,
            color: isFertilizer ? Colors.green : Colors.orange.shade800,
          ),
        ),
        title: Text(
          '${treatment.cropName}: ${treatment.productName}',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          '${treatment.quantity} ${treatment.unit} • ${DateFormat('MMM dd, yyyy').format(treatment.appliedDate)}',
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline, color: Colors.red),
          onPressed: () => TreatmentService().deleteTreatment(treatment.id),
        ),
      ),
    );
  }
}

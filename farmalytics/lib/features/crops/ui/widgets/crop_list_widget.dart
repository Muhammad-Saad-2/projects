import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:farmalytics/features/crops/models/crop_model.dart';
import 'package:farmalytics/features/crops/services/crop_service.dart';
import 'package:farmalytics/features/crops/ui/crop_detail_screen.dart';

class CropListWidget extends StatelessWidget {
  final String userId;
  const CropListWidget({super.key, required this.userId});

  @override
  Widget build(BuildContext context) {
    final cropService = CropService();

    return StreamBuilder<List<Crop>>(
      stream: cropService.getActiveCrops(userId),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }

        final crops = snapshot.data ?? [];

        if (crops.isEmpty) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(40.0),
              child: Column(
                children: [
                  Icon(Icons.eco_outlined, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No active crops yet.\nTap the + button to add one!',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ),
          );
        }

        return ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: crops.length,
          itemBuilder: (context, index) {
            final crop = crops[index];
            return Card(
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: BorderSide(color: Colors.green.shade100),
              ),
              child: ListTile(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => CropDetailScreen(crop: crop),
                    ),
                  );
                },
                leading: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.eco, color: Color(0xFF2E7D32)),
                ),
                title: Text(
                  crop.name,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Text(
                  'Sown: ${DateFormat('MMM dd').format(crop.sowingDate)} • ${crop.stage.displayName}',
                ),
                trailing: PopupMenuButton<String>(
                  onSelected: (value) async {
                    if (value == 'harvest') {
                      await cropService.archiveCrop(crop.id);
                    } else if (value == 'delete') {
                      await cropService.deleteCrop(crop.id);
                    }
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'harvest',
                      child: Text('Mark as Harvested'),
                    ),
                    const PopupMenuItem(
                      value: 'delete',
                      child: Text('Delete', style: TextStyle(color: Colors.red)),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}

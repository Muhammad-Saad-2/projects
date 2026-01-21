import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/crop_model.dart';

class CropService {
  final FirebaseFirestore _firestore;

  CropService({FirebaseFirestore? firestore})
      : _firestore = firestore ?? FirebaseFirestore.instance;

  // Add a new crop
  Future<void> addCrop(Crop crop) async {
    await _firestore.collection('crops').add(crop.toFirestore());
  }

  // Get active crops for a user
  Stream<List<Crop>> getActiveCrops(String userId) {
    return _firestore
        .collection('crops')
        .where('userId', isEqualTo: userId)
        .where('isArchived', isEqualTo: false)
        .snapshots()
        .map((snapshot) {
      final crops = snapshot.docs.map((doc) => Crop.fromFirestore(doc)).toList();
      crops.sort((a, b) => b.sowingDate.compareTo(a.sowingDate));
      return crops;
    });
  }

  // Get archived crops for a user
  Stream<List<Crop>> getArchivedCrops(String userId) {
    return _firestore
        .collection('crops')
        .where('userId', isEqualTo: userId)
        .where('isArchived', isEqualTo: true)
        .snapshots()
        .map((snapshot) {
      final crops = snapshot.docs.map((doc) => Crop.fromFirestore(doc)).toList();
      crops.sort((a, b) => b.sowingDate.compareTo(a.sowingDate));
      return crops;
    });
  }

  // Update crop stage
  Future<void> updateCropStage(String cropId, CropStage newStage) async {
    await _firestore.collection('crops').doc(cropId).update({
      'stage': newStage.name,
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  // Archive a crop (Mark as Harvested)
  Future<void> archiveCrop(String cropId) async {
    await _firestore.collection('crops').doc(cropId).update({
      'isArchived': true,
      'stage': CropStage.harvest.name,
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  // Delete a crop
  Future<void> deleteCrop(String cropId) async {
    await _firestore.collection('crops').doc(cropId).delete();
  }
}

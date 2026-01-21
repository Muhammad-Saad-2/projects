import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/treatment_model.dart';

class TreatmentService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<void> addTreatment(Treatment treatment) async {
    await _firestore.collection('treatments').add(treatment.toFirestore());
  }

  Stream<List<Treatment>> getTreatments(String userId) {
    return _firestore
        .collection('treatments')
        .where('userId', isEqualTo: userId)
        .snapshots()
        .map((snapshot) {
      final treatments =
          snapshot.docs.map((doc) => Treatment.fromFirestore(doc)).toList();
      treatments.sort((a, b) => b.appliedDate.compareTo(a.appliedDate));
      return treatments;
    });
  }

  Future<void> deleteTreatment(String id) async {
    await _firestore.collection('treatments').doc(id).delete();
  }
}

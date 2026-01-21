import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/watering_model.dart';

class WateringService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Future<DocumentReference> addSchedule(WateringSchedule schedule) async {
    return await _firestore.collection('watering_schedules').add(schedule.toFirestore());
  }

  Stream<List<WateringSchedule>> getSchedules(String userId) {
    return _firestore
        .collection('watering_schedules')
        .where('userId', isEqualTo: userId)
        .snapshots()
        .map((snapshot) =>
            snapshot.docs.map((doc) => WateringSchedule.fromFirestore(doc)).toList());
  }

  Future<void> deleteSchedule(String id) async {
    await _firestore.collection('watering_schedules').doc(id).delete();
  }
}

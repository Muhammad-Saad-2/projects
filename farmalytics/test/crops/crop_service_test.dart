import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:fake_cloud_firestore/fake_cloud_firestore.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:farmalytics/features/crops/models/crop_model.dart';
import 'package:farmalytics/features/crops/services/crop_service.dart';

void main() {
  late FakeFirebaseFirestore firestore;
  late CropService service;

  setUp(() {
    firestore = FakeFirebaseFirestore();
    service = CropService(firestore: firestore);
  });

  test('addCrop adds a crop to Firestore', () async {
    final crop = Crop(
      id: '',
      userId: 'user123',
      name: 'Tomato',
      fieldName: 'Plot A',
      sowingDate: DateTime(2024, 1, 1),
      stage: CropStage.seedling,
    );

    await service.addCrop(crop);

    final snapshot = await firestore.collection('crops').get();
    expect(snapshot.docs.length, 1);
    expect(snapshot.docs.first['name'], 'Tomato');
    expect(snapshot.docs.first['fieldName'], 'Plot A');
    expect(snapshot.docs.first['userId'], 'user123');
  });

  test('getActiveCrops returns only non-archived crops for the user', () async {
    await firestore.collection('crops').add({
      'userId': 'user1',
      'name': 'Active Crop',
      'isArchived': false,
      'sowingDate': Timestamp.fromDate(DateTime.now()),
      'stage': 'seedling',
    });
    await firestore.collection('crops').add({
      'userId': 'user1',
      'name': 'Archived Crop',
      'isArchived': true,
      'sowingDate': Timestamp.fromDate(DateTime.now()),
      'stage': 'harvest',
    });
    await firestore.collection('crops').add({
      'userId': 'user2',
      'name': 'Other User Crop',
      'isArchived': false,
      'sowingDate': Timestamp.fromDate(DateTime.now()),
      'stage': 'seedling',
    });

    final crops = await service.getActiveCrops('user1').first;

    expect(crops.length, 1);
    expect(crops.first.name, 'Active Crop');
  });

  test('archiveCrop marks crop as archived and stage as harvest', () async {
    final docRef = await firestore.collection('crops').add({
      'userId': 'user1',
      'name': 'Tomato',
      'isArchived': false,
      'stage': 'vegetative',
      'sowingDate': Timestamp.fromDate(DateTime.now()),
    });

    await service.archiveCrop(docRef.id);

    final updatedDoc = await firestore.collection('crops').doc(docRef.id).get();
    expect(updatedDoc['isArchived'], true);
    expect(updatedDoc['stage'], 'harvest');
  });
}

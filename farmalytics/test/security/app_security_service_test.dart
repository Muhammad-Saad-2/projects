import 'package:flutter_test/flutter_test.dart';
import 'package:farmalytics/features/security/app_security_service.dart';
import 'package:fake_cloud_firestore/fake_cloud_firestore.dart';

void main() {
  group('AppSecurityService Tests', () {
    late FakeFirebaseFirestore fakeFirestore;
    late AppSecurityService service;

    setUp(() {
      fakeFirestore = FakeFirebaseFirestore();
      service = AppSecurityService(firestore: fakeFirestore);
    });

    test('Initial state is loading and active', () {
      expect(service.isActive, true);
      expect(service.isLoading, true);
    });

    test('verifyAccess sets isActive to true when Firestore doc is active', () async {
      await fakeFirestore.collection('app_config').doc('status').set({
        'is_active': true,
        'message': 'All good',
      });

      await service.verifyAccess();

      expect(service.isActive, true);
      expect(service.isLoading, false);
      expect(service.message, 'All good');
    });

    test('verifyAccess sets isActive to false when Firestore doc is inactive', () async {
      await fakeFirestore.collection('app_config').doc('status').set({
        'is_active': false,
        'message': 'Expired',
      });

      await service.verifyAccess();

      expect(service.isActive, false);
      expect(service.isLoading, false);
      expect(service.message, 'Expired');
    });

    test('verifyAccess sets isActive to false and shows error message on failure', () async {
      // simulate missing doc (service logic handles this as false/missing config)
      await service.verifyAccess();

      expect(service.isActive, false);
      expect(service.message, 'Application configuration missing. Please contact support.');
    });
  });
}

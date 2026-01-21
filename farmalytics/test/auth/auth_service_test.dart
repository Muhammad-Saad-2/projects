import 'package:flutter_test/flutter_test.dart';
import 'package:farmalytics/features/auth/auth_service.dart';
import 'package:firebase_auth_mocks/firebase_auth_mocks.dart';
import 'package:google_sign_in_mocks/google_sign_in_mocks.dart';
import 'package:fake_cloud_firestore/fake_cloud_firestore.dart';

void main() {
  group('AuthService Tests', () {
    late MockFirebaseAuth auth;
    late MockGoogleSignIn googleSignIn;
    late FakeFirebaseFirestore firestore;
    late AuthService service;

    setUp(() {
      auth = MockFirebaseAuth();
      googleSignIn = MockGoogleSignIn();
      firestore = FakeFirebaseFirestore();
      service = AuthService(
        auth: auth,
        firestore: firestore,
        googleSignIn: googleSignIn,
      );
    });

    test('signUpWithEmail creates user and syncs profile', () async {
      final credential = await service.signUpWithEmail(
        'test@example.com',
        'password123',
        'Test User',
      );

      expect(credential?.user?.email, 'test@example.com');
      
      final userDoc = await firestore.collection('users').doc(credential!.user!.uid).get();
      expect(userDoc.exists, true);
      expect(userDoc.data()?['name'], 'Test User');
    });

    test('signInWithEmail returns user credential', () async {
      await auth.createUserWithEmailAndPassword(
        email: 'test@example.com',
        password: 'password123',
      );

      final credential = await service.signInWithEmail(
        'test@example.com',
        'password123',
      );

      expect(credential?.user?.email, 'test@example.com');
    });

    test('signOut signs out from firebase and google', () async {
      await service.signOut();
      expect(auth.currentUser, isNull);
    });
  });
}

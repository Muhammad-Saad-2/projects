import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';

class AppSecurityService extends ChangeNotifier {
  bool _isActive = true;
  String _message = 'This application has been disabled.';
  bool _isLoading = true;

  bool get isActive => _isActive;
  String get message => _message;
  bool get isLoading => _isLoading;

  final FirebaseFirestore _firestore;

  AppSecurityService({FirebaseFirestore? firestore})
      : _firestore = firestore ?? FirebaseFirestore.instance;

  Future<void> verifyAccess() async {
    _isLoading = true;
    notifyListeners();

    try {
      final doc = await _firestore.collection('app_config').doc('status').get();
      
      if (doc.exists) {
        final data = doc.data();
        if (data != null) {
          _isActive = data['is_active'] ?? true;
          _message = data['message'] ?? 'This application has been disabled.';
        }
      } else {
        // If doc doesn't exist, we default to active for now, 
        // but constitution says "Lock if unreachable/missing" might be safer.
        // Let's stick to the spec: "Fetch app_config/status".
        // If it doesn't exist, it might be an error.
        _isActive = false;
        _message = 'Application configuration missing. Please contact support.';
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error verifying access: $e');
      }
      // Fail-safe: Lock if error occurs (as per requirements.md recommendation)
      _isActive = false;
      _message = 'Security check failed. Please check your internet connection.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}

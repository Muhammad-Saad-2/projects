import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

enum WateringFrequency { daily, alternate, custom }

class WateringSchedule {
  final String id;
  final String userId;
  final String cropId;
  final String cropName;
  final WateringFrequency frequency;
  final TimeOfDay startTime;
  final DateTime startDate;

  WateringSchedule({
    required this.id,
    required this.userId,
    required this.cropId,
    required this.cropName,
    required this.frequency,
    required this.startTime,
    required this.startDate,
  });

  factory WateringSchedule.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return WateringSchedule(
      id: doc.id,
      userId: data['userId'] ?? '',
      cropId: data['cropId'] ?? '',
      cropName: data['cropName'] ?? '',
      frequency: WateringFrequency.values.firstWhere(
        (e) => e.name == data['frequency'],
        orElse: () => WateringFrequency.daily,
      ),
      startTime: TimeOfDay(
        hour: data['startHour'] ?? 8,
        minute: data['startMinute'] ?? 0,
      ),
      startDate: (data['startDate'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'userId': userId,
      'cropId': cropId,
      'cropName': cropName,
      'frequency': frequency.name,
      'startHour': startTime.hour,
      'startMinute': startTime.minute,
      'startDate': Timestamp.fromDate(startDate),
      'updatedAt': FieldValue.serverTimestamp(),
    };
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WateringSchedule &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;
}

import 'package:cloud_firestore/cloud_firestore.dart';

enum TreatmentType { fertilizer, pesticide }

class Treatment {
  final String id;
  final String userId;
  final String cropId;
  final String cropName;
  final TreatmentType type;
  final String productName;
  final double quantity;
  final String unit;
  final DateTime appliedDate;

  Treatment({
    required this.id,
    required this.userId,
    required this.cropId,
    required this.cropName,
    required this.type,
    required this.productName,
    required this.quantity,
    required this.unit,
    required this.appliedDate,
  });

  factory Treatment.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return Treatment(
      id: doc.id,
      userId: data['userId'] ?? '',
      cropId: data['cropId'] ?? '',
      cropName: data['cropName'] ?? '',
      type: TreatmentType.values.firstWhere(
        (e) => e.name == data['type'],
        orElse: () => TreatmentType.fertilizer,
      ),
      productName: data['productName'] ?? '',
      quantity: (data['quantity'] as num).toDouble(),
      unit: data['unit'] ?? '',
      appliedDate: (data['appliedDate'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'userId': userId,
      'cropId': cropId,
      'cropName': cropName,
      'type': type.name,
      'productName': productName,
      'quantity': quantity,
      'unit': unit,
      'appliedDate': Timestamp.fromDate(appliedDate),
      'createdAt': FieldValue.serverTimestamp(),
    };
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Treatment &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;
}

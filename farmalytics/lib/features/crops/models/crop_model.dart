import 'package:cloud_firestore/cloud_firestore.dart';

enum CropStage {
  seedling,
  vegetative,
  flowering,
  harvest;

  String get displayName {
    switch (this) {
      case CropStage.seedling: return 'Seedling';
      case CropStage.vegetative: return 'Vegetative';
      case CropStage.flowering: return 'Flowering';
      case CropStage.harvest: return 'Harvest';
    }
  }
}

class Crop {
  final String id;
  final String userId;
  final String name;
  final String? fieldName;
  final DateTime sowingDate;
  final DateTime? expectedHarvestDate;
  final CropStage stage;
  final bool isArchived;

  Crop({
    required this.id,
    required this.userId,
    required this.name,
    this.fieldName,
    required this.sowingDate,
    this.expectedHarvestDate,
    required this.stage,
    this.isArchived = false,
  });

  factory Crop.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return Crop(
      id: doc.id,
      userId: data['userId'] ?? '',
      name: data['name'] ?? '',
      fieldName: data['fieldName'],
      sowingDate: (data['sowingDate'] as Timestamp).toDate(),
      expectedHarvestDate: data['expectedHarvestDate'] != null
          ? (data['expectedHarvestDate'] as Timestamp).toDate()
          : null,
      stage: CropStage.values.firstWhere(
        (e) => e.name == data['stage'],
        orElse: () => CropStage.seedling,
      ),
      isArchived: data['isArchived'] ?? false,
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'userId': userId,
      'name': name,
      'fieldName': fieldName,
      'sowingDate': Timestamp.fromDate(sowingDate),
      'expectedHarvestDate': expectedHarvestDate != null
          ? Timestamp.fromDate(expectedHarvestDate!)
          : null,
      'stage': stage.name,
      'isArchived': isArchived,
      'updatedAt': FieldValue.serverTimestamp(),
    };
  }

  Crop copyWith({
    String? name,
    String? fieldName,
    DateTime? sowingDate,
    DateTime? expectedHarvestDate,
    CropStage? stage,
    bool? isArchived,
  }) {
    return Crop(
      id: id,
      userId: userId,
      name: name ?? this.name,
      fieldName: fieldName ?? this.fieldName,
      sowingDate: sowingDate ?? this.sowingDate,
      expectedHarvestDate: expectedHarvestDate ?? this.expectedHarvestDate,
      stage: stage ?? this.stage,
      isArchived: isArchived ?? this.isArchived,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Crop &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;
}

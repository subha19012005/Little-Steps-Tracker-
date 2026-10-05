class GrowthRecord {
  final DateTime date;
  final double height;
  final double weight;

  GrowthRecord({
    required this.date,
    required this.height,
    required this.weight,
  });

  double get bmi {
    final heightInMetres = height / 100;

    if (heightInMetres <= 0) {
      return 0;
    }

    return weight / (heightInMetres * heightInMetres);
  }

  factory GrowthRecord.fromJson(Map<String, dynamic> json) {
    return GrowthRecord(
      date: DateTime.parse(json['date']),
      height: (json['height'] as num).toDouble(),
      weight: (json['weight'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date.toIso8601String(),
      'height': height,
      'weight': weight,
    };
  }
}
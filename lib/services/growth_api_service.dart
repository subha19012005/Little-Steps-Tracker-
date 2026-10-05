import 'package:dio/dio.dart';

import '../models/growth_record.dart';

class GrowthApiService {
  final Dio dio = Dio(
    BaseOptions(
      baseUrl: "http://YOUR_API_IP:8000",
      headers: {
        "Content-Type": "application/json",
      },
    ),
  );

  Future<void> saveGrowthRecord({
    required String childId,
    required GrowthRecord record,
  }) async {
    try {
      await dio.post(
        "/growth",
        data: {
          "child_id": childId,
          "date": record.date.toIso8601String(),
          "height": record.height,
          "weight": record.weight,
        },
      );
    } on DioException catch (e) {
      throw Exception(
        "Failed to save growth record: ${e.message}",
      );
    }
  }

  Future<List<GrowthRecord>> getGrowthHistory(
    String childId,
  ) async {
    try {
      final response = await dio.get(
        "/growth/$childId",
      );

      final List data = response.data;

      return data
          .map(
            (item) => GrowthRecord.fromJson(item),
          )
          .toList();
    } on DioException catch (e) {
      throw Exception(
        "Failed to load growth history: ${e.message}",
      );
    }
  }
}
import 'package:flutter/material.dart';

import '../models/growth_record.dart';
import '../widgets/growth_chart.dart';

class GrowthHistoryScreen extends StatefulWidget {
  final String childName;
  final GrowthRecord? newRecord;

  const GrowthHistoryScreen({
    super.key,
    required this.childName,
    this.newRecord,
  });

  @override
  State<GrowthHistoryScreen> createState() =>
      _GrowthHistoryScreenState();
}

class _GrowthHistoryScreenState
    extends State<GrowthHistoryScreen> {

  late List<GrowthRecord> records;

  @override
  void initState() {
    super.initState();

    records = [
      GrowthRecord(
        date: DateTime(2026, 9, 29),
        height: 95.2,
        weight: 14.1,
      ),
      GrowthRecord(
        date: DateTime(2026, 8, 29),
        height: 93.8,
        weight: 13.7,
      ),
    ];

    // Add newly saved record
    if (widget.newRecord != null) {
      records.insert(0, widget.newRecord!);
    }
  }

  String formatDate(DateTime date) {
    return "${date.day.toString().padLeft(2, '0')} "
        "${_monthName(date.month)} "
        "${date.year}";
  }

  String _monthName(int month) {
    const months = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];

    return months[month - 1];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Growth History"),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.childName,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 20),

            const Text(
              "Growth History",
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 10),

            // HISTORY CARDS
            ListView.builder(
              shrinkWrap: true,
              physics:
                  const NeverScrollableScrollPhysics(),
              itemCount: records.length,
              itemBuilder: (context, index) {
                final record = records[index];

                return Card(
                  margin:
                      const EdgeInsets.only(bottom: 12),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        Text(
                          formatDate(record.date),
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),

                        const SizedBox(height: 10),

                        Text(
                          "Height: ${record.height.toStringAsFixed(1)} cm",
                        ),

                        const SizedBox(height: 5),

                        Text(
                          "Weight: ${record.weight.toStringAsFixed(1)} kg",
                        ),

                        const SizedBox(height: 5),

                        Text(
                          "BMI: ${record.bmi.toStringAsFixed(1)}",
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),

            const SizedBox(height: 20),

            const Text(
              "Height over time",
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 10),

            GrowthChart(
              records: records,
              showHeight: true,
            ),

            const SizedBox(height: 30),

            const Text(
              "Weight over time",
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 10),

            GrowthChart(
              records: records,
              showHeight: false,
            ),
          ],
        ),
      ),
    );
  }
}
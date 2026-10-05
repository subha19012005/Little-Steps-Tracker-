import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../models/growth_record.dart';

class GrowthChart extends StatelessWidget {
  final List<GrowthRecord> records;
  final bool showHeight;

  const GrowthChart({
    super.key,
    required this.records,
    required this.showHeight,
  });

  @override
  Widget build(BuildContext context) {
    final sortedRecords = [...records]
      ..sort((a, b) => a.date.compareTo(b.date));

    final spots = <FlSpot>[];

    for (int i = 0; i < sortedRecords.length; i++) {
      final value = showHeight
          ? sortedRecords[i].height
          : sortedRecords[i].weight;

      spots.add(
        FlSpot(
          i.toDouble(),
          value,
        ),
      );
    }

    if (spots.isEmpty) {
      return const SizedBox(
        height: 250,
        child: Center(
          child: Text("No growth data available"),
        ),
      );
    }

    return SizedBox(
      height: 250,
      child: LineChart(
        LineChartData(
          gridData: const FlGridData(
            show: true,
          ),

          titlesData: FlTitlesData(
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  final index = value.toInt();

                  if (index < 0 ||
                      index >= sortedRecords.length) {
                    return const SizedBox();
                  }

                  final date =
                      sortedRecords[index].date;

                  return Text(
                    "${date.day}/${date.month}",
                    style: const TextStyle(
                      fontSize: 10,
                    ),
                  );
                },
              ),
            ),

            leftTitles: const AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
              ),
            ),

            topTitles: const AxisTitles(
              sideTitles: SideTitles(
                showTitles: false,
              ),
            ),

            rightTitles: const AxisTitles(
              sideTitles: SideTitles(
                showTitles: false,
              ),
            ),
          ),

          borderData: FlBorderData(
            show: true,
          ),

          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              barWidth: 3,
              dotData: const FlDotData(
                show: true,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
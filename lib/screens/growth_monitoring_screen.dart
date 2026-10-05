import 'package:flutter/material.dart';

import '../models/growth_record.dart';
import 'growth_history_screen.dart';

class GrowthMonitoringScreen extends StatefulWidget {
  final String childName;

  const GrowthMonitoringScreen({
    super.key,
    required this.childName,
  });

  @override
  State<GrowthMonitoringScreen> createState() =>
      _GrowthMonitoringScreenState();
}

class _GrowthMonitoringScreenState
    extends State<GrowthMonitoringScreen> {
  final TextEditingController heightController =
      TextEditingController();

  final TextEditingController weightController =
      TextEditingController();

  DateTime selectedDate = DateTime.now();

  bool isSaving = false;

  String? heightError;
  String? weightError;

  Future<void> selectDate() async {
    final DateTime? pickedDate = await showDatePicker(
      context: context,
      initialDate: selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );

    if (pickedDate != null) {
      setState(() {
        selectedDate = pickedDate;
      });
    }
  }

  Future<void> saveMeasurement() async {
    setState(() {
      heightError = null;
      weightError = null;
    });

    final double? height =
        double.tryParse(heightController.text.trim());

    final double? weight =
        double.tryParse(weightController.text.trim());

    bool hasError = false;

    if (height == null || height <= 0) {
      setState(() {
        heightError = "Enter a valid height";
      });
      hasError = true;
    }

    if (weight == null || weight <= 0) {
      setState(() {
        weightError = "Enter a valid weight";
      });
      hasError = true;
    }

    if (hasError) {
      return;
    }

    setState(() {
      isSaving = true;
    });

    // Temporary local record.
    // Later this will be sent to Person 3's FastAPI.
    final GrowthRecord record = GrowthRecord(
      date: selectedDate,
      height: height!,
      weight: weight!,
    );

    await Future.delayed(
      const Duration(milliseconds: 500),
    );

    if (!mounted) return;

    setState(() {
      isSaving = false;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Growth measurement saved"),
        backgroundColor: Colors.green,
      ),
    );

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => GrowthHistoryScreen(
          childName: widget.childName,
          newRecord: record,
        ),
      ),
    );
  }

  @override
  void dispose() {
    heightController.dispose();
    weightController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Growth Monitoring"),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
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

            const SizedBox(height: 8),

            const Text(
              "Add Growth Measurement",
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey,
              ),
            ),

            const SizedBox(height: 30),

            // DATE
            const Text(
              "Date",
              style: TextStyle(
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 8),

            InkWell(
              onTap: selectDate,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 16,
                ),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment:
                      MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "${selectedDate.day.toString().padLeft(2, '0')}/"
                      "${selectedDate.month.toString().padLeft(2, '0')}/"
                      "${selectedDate.year}",
                    ),
                    const Icon(Icons.calendar_today),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // HEIGHT
            TextField(
              controller: heightController,
              keyboardType:
                  const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: InputDecoration(
                labelText: "Height (cm)",
                hintText: "Enter height",
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.height),
                errorText: heightError,
              ),
            ),

            const SizedBox(height: 20),

            // WEIGHT
            TextField(
              controller: weightController,
              keyboardType:
                  const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: InputDecoration(
                labelText: "Weight (kg)",
                hintText: "Enter weight",
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.monitor_weight),
                errorText: weightError,
              ),
            ),

            const SizedBox(height: 30),

            // SAVE BUTTON
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: isSaving
                    ? null
                    : saveMeasurement,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
                child: isSaving
                    ? const CircularProgressIndicator(
                        color: Colors.white,
                      )
                    : const Text(
                        "SAVE",
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
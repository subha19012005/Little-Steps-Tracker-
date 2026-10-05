import 'package:flutter/material.dart';

import 'growth_monitoring_screen.dart';
import 'growth_history_screen.dart';

class ChildProfileScreen extends StatelessWidget {
  const ChildProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const String childName = "Arun";

    return Scaffold(
      appBar: AppBar(
        title: const Text("Child Profile"),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircleAvatar(
                radius: 45,
                child: Icon(
                  Icons.child_care,
                  size: 50,
                ),
              ),

              const SizedBox(height: 15),

              const Text(
                childName,
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 30),

              // GROWTH MONITORING BUTTON
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) =>
                            const GrowthMonitoringScreen(
                          childName: childName,
                        ),
                      ),
                    );
                  },
                  child: const Text(
                    "Growth Monitoring",
                    style: TextStyle(fontSize: 17),
                  ),
                ),
              ),

              const SizedBox(height: 15),

              // GROWTH HISTORY BUTTON
              SizedBox(
                width: double.infinity,
                height: 50,
                child: OutlinedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) =>
                            const GrowthHistoryScreen(
                          childName: childName,
                        ),
                      ),
                    );
                  },
                  child: const Text(
                    "Growth History",
                    style: TextStyle(fontSize: 17),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
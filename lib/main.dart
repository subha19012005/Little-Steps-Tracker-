import 'package:flutter/material.dart';

import 'screens/child_profile_screen.dart';

void main() {
  runApp(const LittleStepsApp());
}

class LittleStepsApp extends StatelessWidget {
  const LittleStepsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Little Steps Tracker",
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const ChildProfileScreen(),
    );
  }
}
import 'package:flutter/material.dart';
import 'screens/dashboard_screen.dart'; // Import the screen!

void main() {
  runApp(const ManhattanApp());
}

class ManhattanApp extends StatelessWidget {
  const ManhattanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Manhattan',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.teal,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      // Point the home page to our new DashboardScreen class
      home: const DashboardScreen(), 
    );
  }
}
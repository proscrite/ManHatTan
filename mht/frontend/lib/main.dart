import 'package:flutter/material.dart';
import 'screens/mode_selection_screen.dart';

void main() {
  runApp(const ManhattanApp());
}

class ManhattanApp extends StatelessWidget {
  const ManhattanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false, // Hides the "Debug" banner in the corner
      title: 'Manhattan',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      // Set the new Hub as the starting screen
      home: const ModeSelectionScreen(),
    );
  }
}

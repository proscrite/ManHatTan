import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'multiple_choice_screen.dart';
import 'written_input_screen.dart';
import 'document_upload_screen.dart';
import 'settings_screen.dart';
import '../services/ingestion_service.dart';

import '../widgets/exercise_card.dart';

class ModeSelectionScreen extends StatefulWidget {
  const ModeSelectionScreen({super.key});

  @override
  State<ModeSelectionScreen> createState() => _ModeSelectionScreenState();
}

class _ModeSelectionScreenState extends State<ModeSelectionScreen> {
  // true = Reverse Translation (Prompt: English -> Answer: Hebrew)
  // false = Direct Translation (Prompt: Hebrew -> Answer: English)
  bool _isReverseTranslation = true;
  @override
  void initState() {
    super.initState();
    // Fetch courses immediately when the Hub opens so global state is ready!
    _initializeGlobalState();
  }

  Future<void> _initializeGlobalState() async {
    try {
      // If we haven't loaded courses yet, fetch them
      if (IngestionService.allCourses.isEmpty) {
        await IngestionService.fetchMyCourses();
        // Optional: if you want the Hub to redraw after finding the active course
        if (mounted) setState(() {}); 
      }
    } catch (e) {
      debugPrint('Error initializing courses: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    // Dynamically calculate the mode strings based on the toggle state
    final String mcMode = _isReverseTranslation ? 'mrt' : 'mdt';
    final String writtenMode = _isReverseTranslation ? 'wrt' : 'wdt';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Manhattan Hub'),
        centerTitle: true,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'Settings & Courses',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              ).then((_) {
                // Refresh the Hub when returning, just in case the active course changed!
                setState(() {});
              });
            },
          ),
        ],
      ),

      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const DocumentUploadScreen()),
          );
        },
        backgroundColor: Colors.teal.shade600,
        tooltip: 'Import Vocabulary',
        child: const Icon(Icons.upload_file, color: Colors.white),
      ),

      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // --- TRANSLATION DIRECTION TOGGLE ---
              const Text(
                'Translation Direction',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Colors.grey),
              ),
              const SizedBox(height: 12),
              SegmentedButton<bool>(
                segments: const [
                  ButtonSegment<bool>(
                    value: true,
                    label: Text('English → Hebrew (RT)'),
                    icon: Icon(Icons.east),
                  ),
                  ButtonSegment<bool>(
                    value: false,
                    label: Text('Hebrew → English (DT)'),
                    icon: Icon(Icons.west),
                  ),
                ],
                selected: {_isReverseTranslation},
                onSelectionChanged: (Set<bool> newSelection) {
                  setState(() {
                    _isReverseTranslation = newSelection.first;
                  });
                },
              ),

              const SizedBox(height: 48),
              const Divider(),
              const SizedBox(height: 24),

              // --- THE CONSOLIDATED EXERCISE CARDS ---

              ExerciseCard(
                title: 'Multiple Choice',
                subtitle: 'Fast-paced 4-button flashcard drills.',
                icon: Icons.grid_view,
                color: Colors.blue.shade600,
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => MultipleChoiceScreen(mode: mcMode)),
                ),
              ),

              const SizedBox(height: 20),

              ExerciseCard(
                title: 'Written Input',
                subtitle: 'Test your spelling and exact recall.',
                icon: Icons.keyboard,
                color: Colors.teal.shade600,
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => WrittenInputScreen(mode: writtenMode)),
                ),
              ),

              const SizedBox(height: 20),

              ExerciseCard(
                title: 'Vocabulary Dashboard',
                subtitle: 'Review your full list and edit entries.',
                icon: Icons.list_alt,
                color: Colors.purple.shade600,
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const DashboardScreen()),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  
}
import 'package:flutter/material.dart';
import '../services/ingestion_service.dart';
import '../models/course.dart';
import 'course_creation_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings'), centerTitle: true),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const Text('Active Course', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.teal)),
          const SizedBox(height: 16),
          
          // Dropdown to manually switch courses
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(12)),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<Course>(
                value: IngestionService.activeCourse,
                isExpanded: true,
                items: IngestionService.allCourses.map((Course c) => 
                  DropdownMenuItem(value: c, child: Text('${c.learningLanguage.toUpperCase()} -> ${c.uiLanguage.toUpperCase()}'))
                ).toList(),
                onChanged: (Course? newVal) {
                  setState(() => IngestionService.activeCourse = newVal);
                },
              ),
            ),
          ),
          
          const SizedBox(height: 24),
          
          OutlinedButton.icon(
            onPressed: () async {
              // Wait for the creation screen to pop back
              final created = await Navigator.push(context, MaterialPageRoute(builder: (_) => const CourseCreationScreen()));
              if (created == true) {
                setState(() {}); // Refresh UI to show new active course
              }
            },
            icon: const Icon(Icons.add),
            label: const Text('Create New Course Track'),
          ),
        ],
      ),
    );
  }
}
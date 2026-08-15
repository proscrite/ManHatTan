import 'package:flutter/material.dart';
import '../services/ingestion_service.dart';
import '../models/course.dart';
import 'course_creation_screen.dart';
import 'document_upload_screen.dart';
import '../services/api_client.dart';
import '../utils/language_helper.dart';
import '../routers/course_flow_router.dart';

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
                value: ApiClient.activeCourse,
                isExpanded: true,
                items: ApiClient.allCourses.map((Course c) => 
                  DropdownMenuItem(
                    value: c,
                     child: Text(LanguageHelper.getFlagAndName(c.learningLanguage) + ' -> ' + LanguageHelper.getFlagAndName(c.uiLanguage)) )
                     ).toList(),
                onChanged: (Course? newVal) {
                  setState(() => ApiClient.activeCourse = newVal);
                },
              ),
            ),
          ),
          
          const SizedBox(height: 24),
          
          OutlinedButton.icon(
            onPressed: () async {
              // Delegate the entire Cold Start sequence to the Master Orchestrator
              await CourseFlowRouter.launchOnboarding(context);
              
              // Refresh Settings when the flow completes so the dropdown shows the newly active course
              if (mounted) {
                setState(() {}); 
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
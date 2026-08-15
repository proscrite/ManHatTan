import 'dart:io';
import 'package:flutter/material.dart';
import '../models/ingestion_intent.dart';
import '../screens/course_creation_screen.dart';
import '../screens/document_upload_screen.dart';
import '../screens/cefr_level_screen.dart';
import '../services/ingestion_service.dart';

class CourseFlowRouter {
  static Future<void> launchOnboarding(BuildContext context, {String? initialLang}) async {
    
    // NODE 1: Language Selection
    final langResult = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => CourseCreationScreen(initialLearningLang: initialLang)),
    );
    if (langResult == null || langResult is! Map<String, String>) return;

    // NODE 2: File Acquisition (Domain A Intent)
    final uploadResult = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const DocumentUploadScreen(intent: IngestionIntent.initialSeed)),
    );
    if (uploadResult == null || uploadResult is! Map<String, dynamic>) return;
    
    // Extract acquired file from Node 2's payload
    final File seedFile = uploadResult['file'];
    final String? seedColor = uploadResult['color'];

    // NODE 3: CEFR Assessment
    final cefrResult = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => CefrLevelScreen(
          learningLang: langResult['learningLang']!,
          uiLang: langResult['uiLang']!,
        ),
      ),
    );
    if (cefrResult == null || cefrResult is! Map<String, String>) return;

    // NODE 4: DEFERRED EXECUTION (API Mutations)
    if (!context.mounted) return;
    
    // Optional: Show a loading overlay while the backend works
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator()),
    );

    try {
      // 1. Create the Course (with CEFR)
      final newCourse = await IngestionService.createCourse(
        cefrResult['learningLang']!,
        cefrResult['uiLang']!,
        cefrLevel: int.tryParse(cefrResult['cefrLevel'] ?? '1') ?? 1,
        fluencyIndex: double.tryParse(cefrResult['fluencyIndex'] ?? '0.0') ?? 0.0,
      );

      // 2. Upload the acquired file to the newly created Course ID
      await IngestionService.uploadDocument(
        newCourse.id, 
        seedFile,
        targetColor: seedColor,
      );

      if (context.mounted) {
        Navigator.pop(context); // Dismiss loading dialog
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Course and vocabulary initialized successfully!'), backgroundColor: Colors.teal),
        );
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context); // Dismiss loading dialog
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Initialization failed: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }
}
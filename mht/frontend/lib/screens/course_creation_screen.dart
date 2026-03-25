import 'package:flutter/material.dart';
import '../services/ingestion_service.dart';

class CourseCreationScreen extends StatefulWidget {
  final String? initialLearningLang;
  
  // If the guardrail triggers this, we pass the detected language so it's pre-filled!
  const CourseCreationScreen({super.key, this.initialLearningLang});

  @override
  State<CourseCreationScreen> createState() => _CourseCreationScreenState();
}

class _CourseCreationScreenState extends State<CourseCreationScreen> {
  late TextEditingController _learningLangController;
  final TextEditingController _uiLangController = TextEditingController(text: 'en'); // Default to English UI
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _learningLangController = TextEditingController(text: widget.initialLearningLang ?? '');
  }

  Future<void> _submit() async {
    if (_learningLangController.text.isEmpty || _uiLangController.text.isEmpty) return;
    
    setState(() => _isLoading = true);
    try {
      await IngestionService.createCourse(
        _learningLangController.text, 
        _uiLangController.text
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Course created successfully!'), backgroundColor: Colors.teal),
        );
        Navigator.pop(context, true); // Return true to signal success to the previous screen
      }
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create New Course'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Learning Language (e.g., de, iw, it)', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _learningLangController,
              decoration: const InputDecoration(border: OutlineInputBorder()),
            ),
            const SizedBox(height: 24),
            
            const Text('Translation Language (e.g., en, es)', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _uiLangController,
              decoration: const InputDecoration(border: OutlineInputBorder()),
            ),
            
            const Spacer(),
            ElevatedButton(
              onPressed: _isLoading ? null : _submit,
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
              child: _isLoading 
                ? const CircularProgressIndicator(color: Colors.white) 
                : const Text('Create & Set as Active', style: TextStyle(fontSize: 16)),
            )
          ],
        ),
      ),
    );
  }
}
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
              readOnly: widget.initialLearningLang != null, // Locks it if it was auto-detected!
              decoration: InputDecoration(
                border: const OutlineInputBorder(),
                filled: widget.initialLearningLang != null,
                fillColor: widget.initialLearningLang != null ? Colors.grey.shade200 : null,
              ),
            ),
            const SizedBox(height: 24),
            
            const Text('Translation Language (e.g., en, es)', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _uiLangController,
              decoration: const InputDecoration(border: OutlineInputBorder()),
            ),
            
            const Spacer(),
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                ElevatedButton.icon(
                  onPressed: () {
                    if (_learningLangController.text.isEmpty || _uiLangController.text.isEmpty) return;
                    // Do NOT call the API here anymore. Just pass the data back to the Upload Screen!
                    Navigator.pop(context, {
                      'learningLang': _learningLangController.text,
                      'uiLang': _uiLangController.text,
                    });
                  },
                  icon: const Icon(Icons.upload_file),
                  label: const Text('Continue to Upload Wordbank', style: TextStyle(fontSize: 16)),
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: null, // Keeps the button disabled!
                  icon: const Icon(Icons.library_books),
                  label: const Text('Select from Template (Coming Soon)'),
                  style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
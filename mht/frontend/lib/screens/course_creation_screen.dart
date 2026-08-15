import 'package:flutter/material.dart';

class CourseCreationScreen extends StatefulWidget {
  final String? initialLearningLang;
  const CourseCreationScreen({super.key, this.initialLearningLang});

  @override
  State<CourseCreationScreen> createState() => _CourseCreationScreenState();
}

class _CourseCreationScreenState extends State<CourseCreationScreen> {
  late TextEditingController _learningLangController;
  final TextEditingController _uiLangController = TextEditingController(text: 'en');

  @override
  void initState() {
    super.initState();
    _learningLangController = TextEditingController(text: widget.initialLearningLang ?? '');
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
              readOnly: widget.initialLearningLang != null,
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
            ElevatedButton.icon(
              onPressed: () {
                if (_learningLangController.text.isEmpty || _uiLangController.text.isEmpty) return;
                
                // PURE SRP: Return data to the Coordinator. No API execution.
                Navigator.pop(context, {
                  'learningLang': _learningLangController.text,
                  'uiLang': _uiLangController.text,
                });
              },
              icon: const Icon(Icons.arrow_forward),
              label: const Text('Continue to File Selection', style: TextStyle(fontSize: 16)),
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
            )
          ],
        ),
      ),
    );
  }
}
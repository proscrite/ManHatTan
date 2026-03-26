import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../models/course.dart';
import '../services/ingestion_service.dart';
import '../widgets/smart_guardrail_card.dart';
import 'course_creation_screen.dart'; 

class DocumentUploadScreen extends StatefulWidget {
  final Map<String, String>? initialPendingCourse;
  const DocumentUploadScreen({super.key, this.initialPendingCourse});

  @override
  State<DocumentUploadScreen> createState() => _DocumentUploadScreenState();
}

class _DocumentUploadScreenState extends State<DocumentUploadScreen> {
  Map<String, String>? _pendingCourse;
  File? _selectedFile;
  Map<String, dynamic>? _analysisResult;
  String? _selectedColor;
  
  bool _isAnalyzing = false;
  bool _isUploading = false;
    @override
    void initState() {
      super.initState();
      // If the guardrail sent us data about a pending course creation, we capture it here!
      if (widget.initialPendingCourse != null) {
        _pendingCourse = widget.initialPendingCourse;
      }
    }

  // Normalizes language codes so 'he' and 'iw' are treated as identical
  String _normalizeLang(String lang) {
    final lower = lang.toLowerCase().trim();
    if (lower == 'he' || lower == 'iw') return 'hebrew';
    return lower;
  }

  // Determines if the detected document language matches the Active Course
  // Determines if the detected document language matches the target course
  bool _isLanguageMatch() {
    if (_analysisResult == null) return true;
    
    // 1. Identify the target language we are comparing against
    final targetCourseLang = _pendingCourse != null 
        ? _pendingCourse!['learningLang']! 
        : (IngestionService.activeCourse?.learningLanguage ?? '');
        
    if (targetCourseLang.isEmpty) return false;

    final activeLang = _normalizeLang(targetCourseLang);

    // 2. Perform the match
    if (_analysisResult!['file_type'] == 'csv') {
      final langs = (_analysisResult!['detected_languages'] as List).map((l) => _normalizeLang(l.toString())).toList();
      return langs.contains(activeLang);
    } else {
      final detectedLang = _normalizeLang(_analysisResult!['detected_language']?.toString() ?? '');
      return detectedLang == activeLang;
    }
  }

  // Extracts the specific language code we need to create a new course
  String _getDetectedLearningLang() {
    if (_analysisResult!['file_type'] == 'csv') {
      final langs = (_analysisResult!['detected_languages'] as List).map((l) => l.toString().toLowerCase()).toList();
      final uiLang = IngestionService.activeCourse?.uiLanguage.toLowerCase() ?? 'en';
      return langs.firstWhere((l) => l != uiLang, orElse: () => langs.first);
    }
    return _analysisResult!['detected_language']?.toString().toLowerCase() ?? 'unknown';
  }

  Future<void> _pickAndAnalyzeFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['html', 'docx', 'csv'],
    );

    if (result != null) {
      final file = File(result.files.single.path!);
      setState(() {
        _selectedFile = file;
        _analysisResult = null;
        _selectedColor = null;
        _isAnalyzing = true;
      });

      try {
        final analysis = await IngestionService.analyzeDocument(file);
        setState(() {
          _analysisResult = analysis;
          _isAnalyzing = false;
          if (analysis['requires_color_selection'] == true && analysis['available_colors'].isNotEmpty) {
            _selectedColor = analysis['available_colors'][0];
          }
        });
      } catch (e) {
        setState(() { _isAnalyzing = false; _selectedFile = null; });
        _showSnackBar('Could not analyze file: $e', isError: true);
      }
    }
  }

  Future<void> _uploadDocument() async {
    if (_selectedFile == null) return;
    if (_analysisResult?['requires_color_selection'] == true && _selectedColor == null) return;

    setState(() => _isUploading = true);

    try {
      // --- JUST-IN-TIME LOGIC ---
      if (_pendingCourse != null) {
        // API Call 1: Create the course
        await IngestionService.createCourse(
          _pendingCourse!['learningLang']!, 
          _pendingCourse!['uiLang']!
        );
        // (IngestionService automatically sets this new course as active!)
        _pendingCourse = null; // Clear the queue
      }
      
      // Fallback check just in case
      if (IngestionService.activeCourse == null) throw Exception("No active course available.");

      // API Call 2: Upload the document
      final result = await IngestionService.uploadDocument(
        IngestionService.activeCourse!.id, 
        _selectedFile!,
        targetColor: _selectedColor,
      );
      
      _showSnackBar(result['message'] ?? 'Import successful!');
      if (mounted) Navigator.pop(context); 
      
    } catch (e) {
      setState(() => _isUploading = false);
      _showSnackBar('Import failed: $e', isError: true);
    }
  }

  void _showSnackBar(String message, {bool isError = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: isError ? Colors.red.shade600 : Colors.teal.shade600),
    );
  }


  @override
  Widget build(BuildContext context) {
    final activeCourse = IngestionService.activeCourse;

    return Scaffold(
      appBar: AppBar(title: const Text('Import Vocabulary'), centerTitle: true),
      body: activeCourse == null 
        ? const Center(child: Text('No active course. Please create one in Settings.'))
        : SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Display the Active Course contextually
                Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                        color: _pendingCourse != null ? Colors.blue.shade50 : Colors.teal.shade50, 
                        borderRadius: BorderRadius.circular(12), 
                        border: Border.all(color: _pendingCourse != null ? Colors.blue.shade200 : Colors.teal.shade200)
                    ),
                    child: Row(
                        children: [
                        Icon(_pendingCourse != null ? Icons.new_releases : Icons.school, 
                            color: _pendingCourse != null ? Colors.blue : Colors.teal),
                        const SizedBox(width: 12),
                        Text(
                            _pendingCourse != null 
                            ? 'Will Create: ${_pendingCourse!['learningLang']!.toUpperCase()} -> ${_pendingCourse!['uiLang']!.toUpperCase()}'
                            : 'Active Course: ${activeCourse.learningLanguage.toUpperCase()} -> ${activeCourse.uiLanguage.toUpperCase()}', 
                            style: TextStyle(
                            fontWeight: FontWeight.bold, 
                            color: _pendingCourse != null ? Colors.blue : Colors.teal, 
                            fontSize: 16
                            )
                        ),
                        ],
                    ),
                    ),
                
                const SizedBox(height: 32),
                
                OutlinedButton.icon(
                  onPressed: (_isUploading || _isAnalyzing) ? null : _pickAndAnalyzeFile,
                  icon: const Icon(Icons.search),
                  label: const Text('Select .html, .docx, or .csv'),
                  style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                ),
                
                if (_isAnalyzing)
                  const Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Center(
                        child: Column(
                            children: [
                                CircularProgressIndicator(), 
                                SizedBox(height: 16), 
                                Text('Analyzing document...', style: TextStyle(color: Colors.grey))
                            ],
                        ),
                    ),
                  ),

                if (_selectedFile != null && !_isAnalyzing && _analysisResult != null) ...[
                  const SizedBox(height: 16),
                  
                  if (!_isLanguageMatch())
                    _buildGuardrailIntegration(),

                    // (We allow upload if languages match OR if they have a pending course queued up)
                   if (_isLanguageMatch() ) ...[
                    
                    if (_analysisResult!['requires_color_selection'] == true) ...[
                      const SizedBox(height: 24),
                      const Text('Select Highlight Color', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(12), border: Border.all(color: Colors.grey.shade300)),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: _selectedColor,
                            isExpanded: true,
                            items: (_analysisResult!['available_colors'] as List<dynamic>).map((c) => DropdownMenuItem(value: c.toString(), child: Text(c.toString().toUpperCase()))).toList(),
                            onChanged: (String? newVal) => setState(() => _selectedColor = newVal),
                          ),
                        ),
                      ),
                    ],

                    const SizedBox(height: 48),

                    ElevatedButton(
                      onPressed: _isUploading ? null : _uploadDocument,
                      style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
                      child: _isUploading
                          ? const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                    SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)),
                                    SizedBox(width: 12),
                                    Text('Translating words...', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                                ],
                            )
                          : const Text('Confirm and Import', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    ),
                  ]
                ],
              ],
            ),
          ),
    );
    
  }

  Widget _buildGuardrailIntegration() {
    // Hide if no analysis is done, or if NO course exists at all
    if (_analysisResult == null) return const SizedBox.shrink();
    if (_pendingCourse == null && IngestionService.activeCourse == null) return const SizedBox.shrink();
    
    // The core check! (This now safely accounts for pending courses)
    if (_isLanguageMatch()) return const SizedBox.shrink();

    final targetLang = _getDetectedLearningLang();
    final backgroundMatch = IngestionService.allCourses.where(
      (c) => _normalizeLang(c.learningLanguage) == _normalizeLang(targetLang)
    ).firstOrNull;

    // Determine what language they were *trying* to upload to
    final currentTargetLang = _pendingCourse != null 
        ? _pendingCourse!['learningLang']! 
        : IngestionService.activeCourse!.learningLanguage;

    return SmartGuardrailCard(
      targetLang: targetLang,
      activeLang: currentTargetLang,
      backgroundMatchLang: backgroundMatch?.learningLanguage,
      onSwitchCourse: () {
        setState(() {
          IngestionService.activeCourse = backgroundMatch;
          _pendingCourse = null; // Important: Clear the pending queue if they switch to an existing course!
        });
        _showSnackBar('Switched Active Course to ${backgroundMatch!.learningLanguage.toUpperCase()}');
      },
      onCreateCourse: () async {
        final result = await Navigator.push(
          context, 
          MaterialPageRoute(builder: (_) => CourseCreationScreen(initialLearningLang: targetLang))
        );
        
        if (result != null && result is Map<String, String>) {
          setState(() {
            _pendingCourse = result; // Overwrite the pending queue with the new correct one!
          });
        }
      },
    );
  }
}
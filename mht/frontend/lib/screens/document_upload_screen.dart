import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../models/ingestion_intent.dart';
import '../services/ingestion_service.dart';
import '../services/api_client.dart';
import '../widgets/smart_guardrail_card.dart';

class DocumentUploadScreen extends StatefulWidget {
  final IngestionIntent intent;

  const DocumentUploadScreen({
    super.key, 
    this.intent = IngestionIntent.update, // Defaults to Domain B
  });

  @override
  State<DocumentUploadScreen> createState() => _DocumentUploadScreenState();
}

class _DocumentUploadScreenState extends State<DocumentUploadScreen> {
  File? _selectedFile;
  Map<String, dynamic>? _analysisResult;
  String? _selectedColor;
  
  bool _isAnalyzing = false;
  bool _isUploading = false;

  String _normalizeLang(String lang) {
    final lower = lang.toLowerCase().trim();
    if (lower == 'he' || lower == 'iw') return 'hebrew';
    return lower;
  }

  bool _isLanguageMatch() {
    if (_analysisResult == null || ApiClient.activeCourse == null) return true;
    
    final activeLang = _normalizeLang(ApiClient.activeCourse!.learningLanguage);

    if (_analysisResult!['file_type'] == 'csv') {
      final langs = (_analysisResult!['detected_languages'] as List).map((l) => _normalizeLang(l.toString())).toList();
      return langs.contains(activeLang);
    } else {
      final detectedLang = _normalizeLang(_analysisResult!['detected_language']?.toString() ?? '');
      return detectedLang == activeLang;
    }
  }

  String _getDetectedLearningLang() {
    if (_analysisResult!['file_type'] == 'csv') {
      final langs = (_analysisResult!['detected_languages'] as List).map((l) => l.toString().toLowerCase()).toList();
      final uiLang = ApiClient.activeCourse?.uiLanguage.toLowerCase() ?? 'en';
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

    // --- DOMAIN A: FILE ACQUISITION ONLY ---
    if (widget.intent == IngestionIntent.initialSeed) {
      // Pass the physical file and metadata back to the Coordinator
      Navigator.pop(context, {
        'file': _selectedFile,
        'color': _selectedColor,
      });
      return; 
    }

    // --- DOMAIN B: DATABASE UPLOAD ---
    setState(() => _isUploading = true);
    try {
      if (ApiClient.activeCourse == null) throw Exception("No active course available.");
      final result = await IngestionService.uploadDocument(
        ApiClient.activeCourse!.id, 
        _selectedFile!,
        targetColor: _selectedColor,
      );
      
      _showSnackBar(result['message'] ?? 'Import successful!');
      if (mounted) Navigator.pop(context, true); 
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

  Widget _buildGuardrailIntegration() {
    if (_analysisResult == null || ApiClient.activeCourse == null) return const SizedBox.shrink();
    if (_isLanguageMatch()) return const SizedBox.shrink();

    // Guardrails only enforce rules during Domain B updates
    if (widget.intent == IngestionIntent.initialSeed) return const SizedBox.shrink();

    final targetLang = _getDetectedLearningLang();
    final backgroundMatch = ApiClient.allCourses.where(
      (c) => _normalizeLang(c.learningLanguage) == _normalizeLang(targetLang)
    ).firstOrNull;

    return SmartGuardrailCard(
      targetLang: targetLang,
      activeLang: ApiClient.activeCourse!.learningLanguage,
      backgroundMatchLang: backgroundMatch?.learningLanguage,
      onSwitchCourse: () {
        setState(() {
          ApiClient.activeCourse = backgroundMatch;
        });
        _showSnackBar('Switched Active Course to ${backgroundMatch!.learningLanguage.toUpperCase()}');
      },
      onCreateCourse: () {
        // THE BAILOUT: Kill this screen and send a routing signal back to the parent
        Navigator.pop(context, {
          'action': 'bailout_to_domain_a',
          'targetLang': targetLang
        });
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final activeCourse = ApiClient.activeCourse;

    return Scaffold(
      appBar: AppBar(title: const Text('Import Vocabulary'), centerTitle: true),
      body: (activeCourse == null && widget.intent == IngestionIntent.update)
        ? const Center(child: Text('No active course. Please create one in Settings.'))
        : SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (widget.intent == IngestionIntent.update && activeCourse != null)
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                        color: Colors.teal.shade50, 
                        borderRadius: BorderRadius.circular(12), 
                        border: Border.all(color: Colors.teal.shade200)
                    ),
                    child: Row(
                        children: [
                        const Icon(Icons.school, color: Colors.teal),
                        const SizedBox(width: 12),
                        Text(
                            'Active Course: ${activeCourse.learningLanguage.toUpperCase()} -> ${activeCourse.uiLanguage.toUpperCase()}', 
                            style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.teal, fontSize: 16)
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
                    child: Center(child: CircularProgressIndicator()),
                  ),

                if (_selectedFile != null && !_isAnalyzing && _analysisResult != null) ...[
                  const SizedBox(height: 16),
                  
                  if (!_isLanguageMatch())
                    _buildGuardrailIntegration(),

                   if (_isLanguageMatch() || widget.intent == IngestionIntent.initialSeed) ...[
                    if (_analysisResult!['requires_color_selection'] == true) ...[
                      const SizedBox(height: 24),
                      const Text('Select Highlight Color', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      DropdownButton<String>(
                        value: _selectedColor,
                        isExpanded: true,
                        items: (_analysisResult!['available_colors'] as List<dynamic>).map((c) => DropdownMenuItem(value: c.toString(), child: Text(c.toString().toUpperCase()))).toList(),
                        onChanged: (String? newVal) => setState(() => _selectedColor = newVal),
                      ),
                    ],

                    const SizedBox(height: 48),

                    ElevatedButton(
                      onPressed: _isUploading ? null : _uploadDocument,
                      style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                      child: _isUploading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('Confirm and Import', style: TextStyle(fontSize: 16)),
                    ),
                  ]
                ],
              ],
            ),
          ),
    );
  }
}
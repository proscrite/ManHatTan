import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../models/course.dart';
import '../services/ingestion_service.dart';

class DocumentUploadScreen extends StatefulWidget {
  const DocumentUploadScreen({super.key});

  @override
  State<DocumentUploadScreen> createState() => _DocumentUploadScreenState();
}

class _DocumentUploadScreenState extends State<DocumentUploadScreen> {
  List<Course> _courses = [];
  Course? _selectedCourse;
  
  File? _selectedFile;
  Map<String, dynamic>? _analysisResult;
  String? _selectedColor;
  
  bool _isLoadingCourses = true;
  bool _isAnalyzing = false;
  bool _isUploading = false;

  @override
  void initState() {
    super.initState();
    _loadCourses();
  }

  Future<void> _loadCourses() async {
    try {
      final courses = await IngestionService.fetchMyCourses();
      setState(() {
        _courses = courses;
        if (_courses.isNotEmpty) _selectedCourse = _courses.first;
        _isLoadingCourses = false;
      });
    } catch (e) {
      setState(() => _isLoadingCourses = false);
      _showSnackBar('Error loading courses', isError: true);
    }
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
          // Auto-select the first color if colors are available
          if (analysis['requires_color_selection'] == true && analysis['available_colors'].isNotEmpty) {
            _selectedColor = analysis['available_colors'][0];
          }
        });
      } catch (e) {
        setState(() {
          _isAnalyzing = false;
          _selectedFile = null; // Reset on failure
        });
        _showSnackBar('Could not analyze file: $e', isError: true);
      }
    }
  }

  Future<void> _uploadDocument() async {
    if (_selectedCourse == null || _selectedFile == null) return;
    
    // Prevent upload if color is required but not selected
    if (_analysisResult?['requires_color_selection'] == true && _selectedColor == null) {
      _showSnackBar('Please select a highlight color', isError: true);
      return;
    }

    setState(() => _isUploading = true);

    try {
      final result = await IngestionService.uploadDocument(
        _selectedCourse!.id, 
        _selectedFile!,
        targetColor: _selectedColor,
      );
      
      _showSnackBar(result['message'] ?? 'Import successful!');
      if (mounted) Navigator.pop(context); // Return to Hub on success!
      
    } catch (e) {
      setState(() => _isUploading = false);
      _showSnackBar('Import failed: $e', isError: true);
    }
  }

  void _showSnackBar(String message, {bool isError = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red.shade600 : Colors.teal.shade600,
      ),
    );
  }

  // --- THE GUARDRAIL CHECK ---
  Widget _buildLanguageWarning() {
    if (_analysisResult == null || _selectedCourse == null) return const SizedBox.shrink();
    
    final detectedLang = _analysisResult!['detected_language']?.toString().toLowerCase();
    // Normalizing Hebrew codes (iw/he) just in case googletrans uses 'he'
    final courseLang = _selectedCourse!.learningLanguage.toLowerCase();
    final isHebrewMatch = (courseLang == 'iw' || courseLang == 'he') && (detectedLang == 'iw' || detectedLang == 'he');
    
    // If it's a CSV, we skip this specific warning for now as it has 2 languages
    if (_analysisResult!['file_type'] == 'csv') return const SizedBox.shrink();

    if (detectedLang != null && detectedLang != courseLang && !isHebrewMatch) {
      return Container(
        margin: const EdgeInsets.only(top: 16),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(color: Colors.orange.shade50, borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.orange.shade200)),
        child: Row(
          children: [
            const Icon(Icons.warning_amber_rounded, color: Colors.orange),
            const SizedBox(width: 12),
            Expanded(child: Text(
              'Warning: This document appears to be in [${detectedLang.toUpperCase()}], but you are importing it to an [${courseLang.toUpperCase()}] course. Are you sure?',
              style: TextStyle(color: Colors.orange.shade900, fontSize: 13),
            )),
          ],
        ),
      );
    }
    return const SizedBox.shrink();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Import Vocabulary'), centerTitle: true),
      body: _isLoadingCourses 
        ? const Center(child: CircularProgressIndicator())
        : SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text('1. Target Course', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(12), border: Border.all(color: Colors.grey.shade300)),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<Course>(
                      value: _selectedCourse,
                      isExpanded: true,
                      items: _courses.map((Course c) => DropdownMenuItem(value: c, child: Text('${c.learningLanguage.toUpperCase()} (to ${c.uiLanguage.toUpperCase()})'))).toList(),
                      onChanged: (Course? newVal) => setState(() => _selectedCourse = newVal),
                    ),
                  ),
                ),
                
                const SizedBox(height: 32),
                
                const Text('2. Select Document', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                
                OutlinedButton.icon(
                  onPressed: (_isUploading || _isAnalyzing) ? null : _pickAndAnalyzeFile,
                  icon: const Icon(Icons.search),
                  label: const Text('Analyze .html, .docx, or .csv'),
                  style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                ),
                
                if (_isAnalyzing)
                  const Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Center(child: Column(
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 16),
                        Text('Analyzing document structure...', style: TextStyle(color: Colors.grey))
                      ],
                    )),
                  ),

                if (_selectedFile != null && !_isAnalyzing && _analysisResult != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: Colors.teal.shade50, borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.teal.shade200)),
                    child: Row(
                      children: [
                        const Icon(Icons.check_circle, color: Colors.teal),
                        const SizedBox(width: 12),
                        Expanded(child: Text('Analyzed: ${_selectedFile!.path.split('/').last}', style: const TextStyle(fontWeight: FontWeight.w500), maxLines: 1, overflow: TextOverflow.ellipsis)),
                        IconButton(icon: const Icon(Icons.close, size: 20, color: Colors.grey), onPressed: () => setState(() { _selectedFile = null; _analysisResult = null; }))
                      ],
                    ),
                  ),

                  _buildLanguageWarning(),

                  // --- DYNAMIC WIZARD STEP ---
                  if (_analysisResult!['requires_color_selection'] == true) ...[
                    const SizedBox(height: 32),
                    const Text('3. Select Highlight Color', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    const Text('Which highlights do you want to extract and translate?', style: TextStyle(fontSize: 13, color: Colors.grey)),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(12), border: Border.all(color: Colors.grey.shade300)),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _selectedColor,
                          isExpanded: true,
                          items: (_analysisResult!['available_colors'] as List<dynamic>).map((color) => DropdownMenuItem(value: color.toString(), child: Text(color.toString().toUpperCase()))).toList(),
                          onChanged: (String? newVal) => setState(() => _selectedColor = newVal),
                        ),
                      ),
                    ),
                  ],

                  if (_analysisResult!['file_type'] == 'csv') ...[
                     const SizedBox(height: 16),
                     Text('Detected Languages: ${_analysisResult!['detected_languages'].join(" <-> ")}', style: TextStyle(color: Colors.teal.shade700, fontWeight: FontWeight.bold)),
                  ],

                  const SizedBox(height: 48),

                  ElevatedButton(
                    onPressed: _isUploading ? null : _uploadDocument,
                    style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
                    child: _isUploading
                        ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Text('Confirm and Import', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
                ],
              ],
            ),
          ),
    );
  }
}
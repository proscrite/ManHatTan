import 'package:flutter/material.dart';

class CefrLevelScreen extends StatefulWidget {
  final String learningLang;
  final String uiLang;

  const CefrLevelScreen({
    super.key,
    required this.learningLang,
    required this.uiLang,
  });

  @override
  State<CefrLevelScreen> createState() => _CefrLevelScreenState();
}

class _CefrLevelScreenState extends State<CefrLevelScreen> {
  bool _showDiagnostic = false;
  String? _baseLevel; // 'A', 'B', or 'C'

  // Standard CEFR Integer Mapping
  final Map<String, int> _cefrMap = {
    'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6
  };

  void _resolveLevel(String levelCode) {
    final int cefrInt = _cefrMap[levelCode] ?? 1; // Default to A1 safely
    
    // Return the complete payload expected by DocumentUploadScreen
    Navigator.pop(context, {
      'learningLang': widget.learningLang,
      'uiLang': widget.uiLang,
      'cefrLevel': cefrInt.toString(),
      'fluencyIndex': '0.0', // Initial invisible seed
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Select Your Level'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: _showDiagnostic ? _buildDiagnosticFlow() : _buildDirectSelection(),
        ),
      ),
    );
  }

  Widget _buildDirectSelection() {
    return Column(
      key: const ValueKey('direct'),
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Do you know your current CEFR level?',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 32),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          alignment: WrapAlignment.center,
          children: _cefrMap.keys.map((level) => ActionChip(
            labelPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            label: Text(level, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            onPressed: () => _resolveLevel(level),
          )).toList(),
        ),
        const Spacer(),
        ElevatedButton.icon(
          onPressed: () => setState(() => _showDiagnostic = true),
          icon: const Icon(Icons.help_outline),
          label: const Text('I am unsure, help me decide'),
          style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
        ),
      ],
    );
  }

  Widget _buildDiagnosticFlow() {
    // QUESTION 2: Sub-level resolution
    if (_baseLevel != null) {
      return Column(
        key: const ValueKey('q2'),
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Let\'s narrow that down. Which sounds more accurate?',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          if (_baseLevel == 'A') ...[
            _DiagnosticOption(text: 'I know basic phrases but struggle to form sentences.', onTap: () => _resolveLevel('A1')),
            _DiagnosticOption(text: 'I can manage simple, routine exchanges on familiar topics.', onTap: () => _resolveLevel('A2')),
          ] else if (_baseLevel == 'B') ...[
            _DiagnosticOption(text: 'I can deal with most travel situations but struggle with complex texts.', onTap: () => _resolveLevel('B1')),
            _DiagnosticOption(text: 'I can understand the main ideas of complex text and converse regularly.', onTap: () => _resolveLevel('B2')),
          ] else ...[
            _DiagnosticOption(text: 'I express myself fluently, but might miss highly localized slang.', onTap: () => _resolveLevel('C1')),
            _DiagnosticOption(text: 'I understand with ease virtually everything heard or read.', onTap: () => _resolveLevel('C2')),
          ],
          const Spacer(),
          TextButton(
            onPressed: () => setState(() => _baseLevel = null),
            child: const Text('Back'),
          )
        ],
      );
    }

    // QUESTION 1: Base level resolution (Targeting B as the central pivot)
    return Column(
      key: const ValueKey('q1'),
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'How would you describe your overall ability?',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 32),
        _DiagnosticOption(
          text: 'I am a beginner. I know basic words and phrases.', 
          onTap: () => setState(() => _baseLevel = 'A')
        ),
        _DiagnosticOption(
          text: 'I am intermediate. I can hold everyday conversations.', 
          onTap: () => setState(() => _baseLevel = 'B')
        ),
        _DiagnosticOption(
          text: 'I am advanced. I can fluently discuss complex topics.', 
          onTap: () => setState(() => _baseLevel = 'C')
        ),
        const Spacer(),
        TextButton(
          onPressed: () => setState(() => _showDiagnostic = false),
          child: const Text('Back'),
        )
      ],
    );
  }
}

class _DiagnosticOption extends StatelessWidget {
  final String text;
  final VoidCallback onTap;

  const _DiagnosticOption({required this.text, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: OutlinedButton(
        onPressed: onTap,
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.all(20),
          alignment: Alignment.centerLeft,
        ),
        child: Text(text, style: const TextStyle(fontSize: 16, color: Colors.black87)),
      ),
    );
  }
}
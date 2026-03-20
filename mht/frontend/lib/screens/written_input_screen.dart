import 'package:flutter/material.dart';
import 'package:intl/intl.dart' hide TextDirection;
import '../services/api_service.dart';

class WrittenInputScreen extends StatefulWidget {
  final String mode; // 'wrt' or 'wdt'
  const WrittenInputScreen({super.key, required this.mode});

  @override
  State<WrittenInputScreen> createState() => _WrittenInputScreenState();
}

class _WrittenInputScreenState extends State<WrittenInputScreen> {
  Map<String, dynamic>? _questionData;
  bool _isLoading = true;
  bool _isChecking = false; // For the RapidFuzz loading state
  final TextEditingController _textController = TextEditingController();
  final FocusNode _focusNode = FocusNode(); // Controls the keyboard!

  @override
  void initState() {
    super.initState();
    _loadNewQuestion();
  }

  @override
  void dispose() {
    _textController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  Future<void> _loadNewQuestion() async {
    setState(() => _isLoading = true);
    _textController.clear();
    
    final data = await ApiService.fetchWrittenExercise(widget.mode);
    setState(() {
      _questionData = data;
      _isLoading = false;
    });
    
    // Auto-summon the keyboard when data loads
    Future.delayed(const Duration(milliseconds: 100), () {
      if (mounted) _focusNode.requestFocus();
    });
  }

  Future<void> _handleSubmit() async {
    if (_textController.text.trim().isEmpty) return;
    
    setState(() => _isChecking = true);
    
    final bool? isCorrect = await ApiService.submitReview(
      _questionData!['vocab_id'].toString(), 
      _textController.text.trim(),
      widget.mode
    );

    setState(() => _isChecking = false);

    if (isCorrect != null) {
      if (isCorrect) {
        // Success! Flash green and load next
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: const Text('✅ Correct!'), backgroundColor: Colors.green.shade700, duration: const Duration(milliseconds: 800)),
        );
        _loadNewQuestion();
      } else {
        // Failure! Show them the right answer and clear the field
        final correctAnswer = _questionData!['correct_answer'];
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Incorrect. The answer was: $correctAnswer'), 
            backgroundColor: Colors.red.shade700, 
            duration: const Duration(seconds: 2)
          ),
        );
        _textController.clear();
        _focusNode.requestFocus(); // Keep keyboard open to try again
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_questionData == null) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Failed to load exercise.', style: TextStyle(fontSize: 18)),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadNewQuestion,
                child: const Text('Try Again'),
              )
            ],
          ),
        ),
      );
    }
    final targetWord = _questionData!['question_text'];
    final bool isPromptRtl = Bidi.hasAnyRtl(targetWord);
    
    // A smart UI trick: If they are doing WIRTE (wrt), they MUST type Hebrew.
    // So we force the text field to RTL immediately, before they even type a letter.
    final bool isInputExpectedRtl = (widget.mode == 'wrt');

    return Scaffold(
      appBar: AppBar(title: const Text('Type the Translation'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              targetWord,
              textAlign: TextAlign.center,
              textDirection: isPromptRtl ? TextDirection.rtl : TextDirection.ltr,
              style: const TextStyle(fontSize: 42, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 48),
            
            TextField(
              controller: _textController,
              focusNode: _focusNode,
              textAlign: isInputExpectedRtl ? TextAlign.right : TextAlign.left,
              textDirection: isInputExpectedRtl ? TextDirection.rtl : TextDirection.ltr,
              style: const TextStyle(fontSize: 24),
              decoration: InputDecoration(
                hintText: isInputExpectedRtl ? 'Type in Hebrew...' : 'Type in English...',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: Colors.grey.shade100,
                suffixIcon: _isChecking 
                  ? const Padding(padding: EdgeInsets.all(12), child: CircularProgressIndicator(strokeWidth: 2))
                  : IconButton(
                      icon: const Icon(Icons.send, color: Colors.teal),
                      onPressed: _handleSubmit,
                    )
              ),
              onSubmitted: (_) => _handleSubmit(),
            ),
          ],
        ),
      ),
    );
  }
}
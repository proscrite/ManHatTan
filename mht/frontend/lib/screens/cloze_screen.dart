import 'dart:math';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart' hide TextDirection;
import '../services/exercise_service.dart';

class ClozeScreen extends StatefulWidget {
  const ClozeScreen({Key? key}) : super(key: key);

  @override
  State<ClozeScreen> createState() => _ClozeScreenState();
}

class _ClozeScreenState extends State<ClozeScreen> {
  bool _isLoading = true;
  Map<String, dynamic>? _exerciseData;
  
  // Interaction State
  String? _selectedOption;
  bool? _isCorrect;
  late bool _isMultipleChoice;

  String? _vocabId; 
  String? _currentMode;
  
  // Written Input Controllers
  final TextEditingController _textController = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    _loadExercise();
  }

  @override
  void dispose() {
    _textController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

    Future<void> _loadExercise() async {
        // 1. Roll the dice for the exercise modality
        final bool isMc = Random().nextBool(); 
        final String currentMode = isMc ? 'aimrt' : 'aiwrt';

        setState(() {
        _isLoading = true;
        _isMultipleChoice = isMc; 
        _currentMode = currentMode;
        });
        
        _textController.clear();

        try {
        // Pass the SRS mode instead of a hardcoded target word
        final result = await ExerciseService.fetchClozeExercise(currentMode);
        
        
        if (result != null && result.containsKey('exercise')) {
            setState(() {
            _vocabId = result['vocab_id']?.toString();
            _exerciseData = result['exercise']; 
            _isLoading = false;
            _selectedOption = null;
            _isCorrect = null;
            });

            if (!_isMultipleChoice) {
            Future.delayed(const Duration(milliseconds: 100), () {
                if (mounted) _focusNode.requestFocus();
            });
            }
        } else {
            throw Exception("Invalid or empty payload received.");
        }
        } catch (e) {
        setState(() => _isLoading = false);
        if (mounted) {
            // This will now catch the 'RATE_LIMIT' exception thrown by the service
            final isRateLimit = e.toString().contains('RATE_LIMIT');
            
            ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Row(
                children: [
                    Icon(isRateLimit ? Icons.timer : Icons.error_outline, color: Colors.white),
                    const SizedBox(width: 12),
                    Expanded(
                    child: Text(isRateLimit
                        ? 'You are learning too fast! The AI needs a 60-second cooldown.'
                        : 'Failed to load CLOZE exercise: $e'),
                    ),
                ],
                ),
                backgroundColor: isRateLimit ? Colors.orange.shade800 : Colors.red.shade700,
                behavior: SnackBarBehavior.floating,
                duration: const Duration(seconds: 4),
            ),
            );
        }
        }
    }

  void _handleAnswer(String answer) async {
    if (_isCorrect != null) return; 

    final blankWord = _exerciseData?['blank_word']?.toString().trim() ?? '';
    final isMatch = answer.trim().toLowerCase() == blankWord.toLowerCase();

    setState(() {
      _selectedOption = answer.trim();
      _isCorrect = isMatch;
    });

    if (_vocabId != null && _currentMode != null) {
      if (_isMultipleChoice) {
        ExerciseService.submitMcReview(_vocabId!, answer.trim(), _currentMode!);
      } else {
        ExerciseService.submitWrittenReview(_vocabId!, answer.trim(), _currentMode!);
      }
    }

    if (isMatch) {
      await Future.delayed(const Duration(milliseconds: 1200));
      if (mounted) _loadExercise();
    } else {
      if (!_isMultipleChoice) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Incorrect. The answer was: $blankWord'),
            backgroundColor: Colors.red.shade700,
            duration: const Duration(seconds: 2),
          ),
        );
        _textController.clear();
        _focusNode.requestFocus();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final String rawTarget = _exerciseData?['sentence_target'] ?? '';
    final String translated = _exerciseData?['sentence_translated'] ?? '';
    final List<String> options = List<String>.from(_exerciseData?['options'] ?? []);
    
    final String displaySentence = _selectedOption != null 
        ? rawTarget.replaceAll(RegExp(r'_+'), _selectedOption!)
        : rawTarget;

    final bool isRtl = Bidi.hasAnyRtl(displaySentence);

    return Scaffold(
      appBar: AppBar(title: const Text('Contextual Cloze'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Spacer(),
            
            Directionality(
              textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
              child: Text(
                displaySentence,
                style: TextStyle(
                  fontSize: 32, 
                  height: 1.5, 
                  fontWeight: FontWeight.bold,
                  color: _isCorrect == null 
                      ? Colors.black87 
                      : (_isCorrect! ? Colors.green.shade700 : Colors.red.shade700)
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 16),
            
            AnimatedOpacity(
              opacity: _selectedOption != null ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 350),
              curve: Curves.easeInOut,
              child: Text(
                translated,
                style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                textAlign: TextAlign.center,
              ),
            ),
            
            const Spacer(),

            if (_isMultipleChoice)
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 1.6,
                children: options.map((option) {
                  return _OptionButton(
                    text: option,
                    isSelected: _selectedOption == option,
                    isCorrect: option == _exerciseData?['blank_word'],
                    anySelected: _selectedOption != null,
                    onPressed: () => _handleAnswer(option),
                  );
                }).toList(),
              )
            else
              TextField(
                controller: _textController,
                focusNode: _focusNode,
                textAlign: isRtl ? TextAlign.right : TextAlign.left,
                textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
                style: const TextStyle(fontSize: 24),
                decoration: InputDecoration(
                  hintText: 'Type the missing word...',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  filled: true,
                  fillColor: Colors.grey.shade100,
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.send, color: Colors.teal),
                    onPressed: () => _handleAnswer(_textController.text),
                  )
                ),
                onSubmitted: (val) => _handleAnswer(val),
              ),

            const SizedBox(height: 24),
            
            if (_selectedOption != null && _isCorrect == false && _isMultipleChoice)
              ElevatedButton(
                onPressed: _loadExercise,
                child: const Text('Skip to Next'),
              ),
          ],
        ),
      ),
    );
  }
}

class _OptionButton extends StatelessWidget {
  final String text;
  final bool isSelected;
  final bool isCorrect;
  final bool anySelected;
  final VoidCallback onPressed;

  const _OptionButton({
    required this.text,
    required this.isSelected,
    required this.isCorrect,
    required this.anySelected,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final bool isRtl = Bidi.hasAnyRtl(text);
    Color buttonColor = Colors.blueGrey.shade50;
    
    if (anySelected) {
      if (isCorrect) {
        buttonColor = Colors.green.shade300;
      } else if (isSelected) {
        buttonColor = Colors.red.shade300;
      }
    }

    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: buttonColor,
        foregroundColor: Colors.black87,
        disabledBackgroundColor: buttonColor,
        disabledForegroundColor: Colors.black87,
        elevation: anySelected ? 0 : 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      onPressed: anySelected ? null : onPressed,
      child: Text(
        text,
        textAlign: TextAlign.center,
        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
        textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
      ),
    );
  }
}
import 'package:flutter/material.dart';
import 'package:intl/intl.dart' hide TextDirection;
import '../services/exercise_service.dart';

// Data model for cleaner code
class McQuestion {
  final String id;
  final String text;
  final List<String> options;
  final String correctAnswer;

  McQuestion({
    required this.id,
    required this.text,
    required this.options,
    required this.correctAnswer,
  });

  factory McQuestion.fromJson(Map<String, dynamic> json) {
    return McQuestion(
      id: json['vocab_id'].toString(),
      text: json['question_text'] ?? '',
      options: List<String>.from(json['options'] ?? []),
      correctAnswer: json['correct_answer'] ?? '',
    );
  }
}

class MultipleChoiceScreen extends StatefulWidget {
  final String mode; // "mrt" or "mdt"
  const MultipleChoiceScreen({super.key, required this.mode});

  @override
  State<MultipleChoiceScreen> createState() => _MultipleChoiceScreenState();
}

class _MultipleChoiceScreenState extends State<MultipleChoiceScreen> {
  McQuestion? _question;
  bool _isLoading = true;
  String? _selectedOption;
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    _loadNewQuestion(isInitial: true);
  }

  Future<void> _loadNewQuestion({bool isInitial = false}) async {
    if (isInitial) {
      setState(() => _isLoading = true);
    }

    try {
      final data = await ExerciseService.fetchMultipleChoice(widget.mode);
      if (mounted) {
        if (data != null) {
          setState(() {
            _question = McQuestion.fromJson(data);
            _selectedOption = null;
            _isLoading = false;
            _hasError = false;
          });
        } else {
          setState(() {
            _hasError = true;
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _hasError = true;
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _handleTap(String tappedWord) async {
    if (_selectedOption != null || _question == null) return;

    setState(() => _selectedOption = tappedWord);

    // Backend validation (Background)
    await ExerciseService.submitMcReview(_question!.id, tappedWord, widget.mode);

    // Visual feedback delay
    await Future.delayed(const Duration(milliseconds: 1200));
    if (mounted) _loadNewQuestion();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_hasError || _question == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Exercise')),
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Failed to load question.'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => _loadNewQuestion(isInitial: true),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Multiple Choice'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const Spacer(),
            Text(
              _question!.text,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 40, fontWeight: FontWeight.bold),
            ),
            const Spacer(),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 1.6,
              children: _question!.options.map((option) {
                return _OptionButton(
                  text: option,
                  isSelected: _selectedOption == option,
                  isCorrect: option == _question!.correctAnswer,
                  anySelected: _selectedOption != null,
                  onPressed: () => _handleTap(option),
                );
              }).toList(),
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

        // Force Flutter to keep your Green/Red colors even when onPressed is null
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

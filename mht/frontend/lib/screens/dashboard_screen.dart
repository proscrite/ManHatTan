import 'package:flutter/material.dart';
import '../services/exercise_service.dart';
import '../services/vocabulary_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<dynamic> _words = [];
  bool _isLoading = false;
  bool _sortByWeakest = false;

  @override
  void initState() {
    super.initState();
    // Optional: Auto-load words when the app starts!
    // loadWords();
  }

  Future<void> loadWords() async {
    setState(() => _isLoading = true);
    final words = await VocabularyService.fetchVocabulary();

    // Sort logic!
    if (_sortByWeakest) {
      // Sorts ascending (0.0 comes before 1.0)
      words.sort((a, b) => (a['p_recall'] as num).compareTo(b['p_recall'] as num));
    }

    setState(() {
      _words = words;
      _isLoading = false;
    });
  }

  // Updated to accept the user's typed text
  Future<void> handleReview(String vocabId, String userAnswer) async {
    setState(() => _isLoading = true);

    // Send to the FastAPI Grading Engine!
    final isCorrect = await ExerciseService.submitWrittenReview(vocabId, userAnswer, 'wrt');

    if (isCorrect != null) {
      // Refresh the list to show the new stats
      await loadWords();

      // Show a highly satisfying pop-up banner!
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              isCorrect ? '✅ Correct!' : '❌ Incorrect. Keep trying!',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            backgroundColor: isCorrect ? Colors.green[700] : Colors.redAccent,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } else {
      setState(() => _isLoading = false);
    }
  }

  void showReviewDialog(Map<String, dynamic> word) {
    // Controller to capture what the user types
    final TextEditingController answerController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          // 1. Ask for the German translation
          title: const Text('Translate to Hebrew', textAlign: TextAlign.center, style: TextStyle(fontSize: 18, color: Colors.grey)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 2. Show the English word
              Text(
                word['word_ul'] ?? 'No translation',
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              // 3. The Text Input Field!

              TextField(
                controller: answerController,
                autofocus: true, // Automatically pops up the keyboard!
                decoration: const InputDecoration(
                  labelText: 'Type the Hebrew word...',
                  border: OutlineInputBorder(),
                ),
                // Allow hitting "Enter" on the keyboard to submit
                onSubmitted: (value) {
                  Navigator.pop(context);
                  handleReview(word['id'], value);
                },
              ),
            ],
          ),
          actionsAlignment: MainAxisAlignment.end,
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context), // Just close without saving
              child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.teal),
              onPressed: () {
                Navigator.pop(context);
                // Pass the typed text to our API
                handleReview(word['id'], answerController.text);
              },
              child: const Text('Submit', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Database Vocab'),
        centerTitle: true,
        actions: [
          // Only show these controls if we actually have words loaded!
          if (_words.isNotEmpty) ...[
            // 1. The Sort Toggle Button
            IconButton(
              icon: Icon(
                _sortByWeakest ? Icons.filter_list_off : Icons.filter_list,
                color: _sortByWeakest ? Colors.greenAccent : Colors.white,
              ),
              tooltip: 'Sort by Weakest',
              onPressed: () {
                setState(() {
                  _sortByWeakest = !_sortByWeakest; // Toggle the boolean
                });
                loadWords(); // Re-fetch and apply the sort!
              },
            ),

            // 2. The Refresh Button
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Refresh Data',
              onPressed: loadWords,
            ),

            // 3. The "Return/Clear" Button
            IconButton(
              icon: const Icon(Icons.close, color: Colors.redAccent),
              tooltip: 'Clear List',
              onPressed: () {
                setState(() {
                  _words = []; // Instantly empties the list!
                  _sortByWeakest = false; // Reset the sort
                });
              },
            ),
          ]
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _words.isEmpty
          ? Center(
        child: ElevatedButton.icon(
          onPressed: loadWords,
          icon: const Icon(Icons.download),
          label: const Text('Fetch Word Database'),
        ),
      )
          : ListView.builder(
        padding: const EdgeInsets.all(8.0),
        itemCount: _words.length,
        itemBuilder: (context, index) {
          final word = _words[index];
          final pRecall = (word['p_recall'] as num).toDouble();
          final scoreColor = Color.lerp(Colors.redAccent, Colors.greenAccent, pRecall);

          return Card(
            child: ListTile(
              title: Text(word['word_ll'] ?? 'Unknown', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
              subtitle: Text(word['word_ul'] ?? ''),
              trailing: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('Recall: ${(pRecall * 100).toInt()}%', style: TextStyle(color: scoreColor, fontWeight: FontWeight.bold)),
                  Text('Seen: ${word['history_seen']}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
              onTap: () => showReviewDialog(word),
            ),
          );
        },
      ),
    );
  }
}
import 'package:flutter/material.dart';
import '../services/api_service.dart'; // Import the service

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<dynamic> _words = [];
  bool _isLoading = false;

  Future<void> loadWords() async {
    setState(() => _isLoading = true);
    
    // Call the newly abstracted API Service!
    final words = await ApiService.fetchVocabulary();
    
    setState(() {
      _words = words;
      _isLoading = false;
    });
  }

  Future<void> handleReview(String vocabId, bool isCorrect) async {
    setState(() => _isLoading = true);
    
    // Call the API service
    final success = await ApiService.submitReview(vocabId, isCorrect);
    
    if (success) {
      await loadWords(); // Refresh the list if successful
    } else {
      setState(() => _isLoading = false);
    }
  }

  void showReviewDialog(Map<String, dynamic> word) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(word['word_ll'] ?? 'Unknown', textAlign: TextAlign.center, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Translation:', style: TextStyle(color: Colors.grey)),
              const SizedBox(height: 8),
              Text(word['word_ul'] ?? 'No translation', style: const TextStyle(fontSize: 18)),
              const Padding(padding: EdgeInsets.only(top: 24.0), child: Text('Did you remember this word?')),
            ],
          ),
          actionsAlignment: MainAxisAlignment.spaceEvenly,
          actions: [
            TextButton(
              onPressed: () { Navigator.pop(context); handleReview(word['id'], false); },
              child: const Text('No (Forgot)', style: TextStyle(color: Colors.redAccent)),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green[700]),
              onPressed: () { Navigator.pop(context); handleReview(word['id'], true); },
              child: const Text('Yes (Remembered)', style: TextStyle(color: Colors.white)),
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
        title: const Text('Schachnovelle Vocab'),
        centerTitle: true,
        actions: [
          if (_words.isNotEmpty) IconButton(icon: const Icon(Icons.refresh), onPressed: loadWords),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _words.isEmpty
              ? Center(
                  child: ElevatedButton.icon(
                    onPressed: loadWords,
                    icon: const Icon(Icons.download),
                    label: const Text('Fetch Schachnovelle Words'),
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
import 'package:flutter/material.dart';
import '../services/vocabulary_service.dart';
import '../services/api_client.dart';
import '../utils/language_helper.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<dynamic> _words = [];
  bool _isLoading = true; // Start true since we auto-load!
  bool _sortByWeakest = false;

  @override
  void initState() {
    super.initState();
    loadWords(); // Auto-load triggered immediately!
  }

  Future<void> loadWords() async {
    setState(() => _isLoading = true);
    final words = await VocabularyService.fetchVocabulary();

    if (_sortByWeakest) {
      words.sort((a, b) => (a['p_recall'] as num).compareTo(b['p_recall'] as num));
    }

    if (mounted) {
      setState(() {
        _words = words;
        _isLoading = false;
      });
    }
  }

  Future<void> handleEditWord(String vocabId, String newLl, String newUl) async {
    if (newLl.trim().isEmpty || newUl.trim().isEmpty) return;

    setState(() => _isLoading = true);

    final success = await VocabularyService.updateWord(vocabId, newLl.trim(), newUl.trim());

    if (success) {
      await loadWords(); // Refresh to show the updated words
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Entry updated successfully!'), backgroundColor: Colors.teal),
        );
      }
    } else {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: const Text('❌ Failed to update entry.'), backgroundColor: Colors.red.shade700),
        );
      }
    }
  }

  void showEditDialog(Map<String, dynamic> word) {
    // Pre-fill the controllers with the existing words
    final TextEditingController llController = TextEditingController(text: word['word_ll']);
    final TextEditingController ulController = TextEditingController(text: word['word_ul']);
    
    final activeCourse = ApiClient.activeCourse;
    final learnLangCode = activeCourse?.learningLanguage.toUpperCase() ?? 'TARGET';
    final uiLangCode = activeCourse?.uiLanguage.toUpperCase() ?? 'BASE';

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Edit Vocabulary', textAlign: TextAlign.center, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: llController,
                decoration: InputDecoration(
                  labelText: 'Learning Language ($learnLangCode)',
                  border: const OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: ulController,
                decoration: InputDecoration(
                  labelText: 'Translation ($uiLangCode)',
                  border: const OutlineInputBorder(),
                ),
              ),
            ],
          ),
          actionsAlignment: MainAxisAlignment.end,
          actions: [
            // LEFT SIDE: The Delete Button
            IconButton(
              icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
              tooltip: 'Delete Word',
              onPressed: () async {
                Navigator.pop(context); // Close dialog
                setState(() => _isLoading = true);
                
                final success = await VocabularyService.deleteWord(word['id'].toString());
                if (success) {
                  await loadWords();
                  if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('🗑️ Word deleted.'), backgroundColor: Colors.redAccent));
                } else {
                  setState(() => _isLoading = false);
                }
              },
            ),
            
            // RIGHT SIDE: Cancel and Save Buttons
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.teal),
                  onPressed: () {
                    Navigator.pop(context);
                    handleEditWord(word['id'].toString(), llController.text, ulController.text);
                  },
                  child: const Text('Save', style: TextStyle(color: Colors.white)),
                ),
              ],
            )
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    // Format the AppBar Title contextually
    final activeCourse = ApiClient.activeCourse;
    final String titleStr = activeCourse != null 
        ? 'Database: ${LanguageHelper.getFlagAndCode(activeCourse.learningLanguage)}'
        : 'Vocabulary Database';

    return Scaffold(
      appBar: AppBar(
        title: Text(titleStr),
        centerTitle: true,
        actions: [
          if (_words.isNotEmpty) ...[
            IconButton(
              icon: Icon(
                _sortByWeakest ? Icons.filter_list_off : Icons.filter_list,
                color: _sortByWeakest ? Colors.greenAccent : Colors.grey,
              ),
              tooltip: 'Sort by Weakest',
              onPressed: () {
                setState(() => _sortByWeakest = !_sortByWeakest);
                loadWords();
              },
            ),
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Refresh Data',
              onPressed: loadWords,
            ),
          ]
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _words.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.library_books_outlined, size: 64, color: Colors.grey.shade400),
                      const SizedBox(height: 16),
                      Text(
                        'No vocabulary found.\nUse the + button on the Hub to import words!',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
                      ),
                    ],
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
                        onTap: () => showEditDialog(word),
                      ),
                    );
                  },
                ),
    );
  }
}
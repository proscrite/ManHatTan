import 'package:flutter/material.dart';
import 'package:frontend/models/ai_content.dart';
import 'package:frontend/services/ai_service.dart';

class AiInsightSheet extends StatefulWidget {
  final String targetWord;
  final String userId;

  const AiInsightSheet({Key? key, required this.targetWord, required this.userId}) : super(key: key);

  @override
  _AiInsightSheetState createState() => _AiInsightSheetState();
}

class _AiInsightSheetState extends State<AiInsightSheet> {
  final AiService _aiService = AiService();
  bool _isLoading = false;
  Map<String, dynamic>? _insightData;
  LLMTaskType _currentTask = LLMTaskType.vocab_fact;

  Future<void> _loadInsight(LLMTaskType type) async {
    setState(() {
      _isLoading = true;
      _currentTask = type;
    });

    try {
      final req = LLMGenerationRequest(
        userId: widget.userId,
        taskType: type,
        targetWord: widget.targetWord,
      );
      final res = await _aiService.fetchInsight(req);
      setState(() => _insightData = res.content);
    } catch (e) {
      setState(() => _insightData = {'error': e.toString()});
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  void initState() {
    super.initState();
    _loadInsight(_currentTask); // Load default insight on open
  }

  Widget _buildInsightContent() {
    if (_insightData == null) return const Text("No data available.");
    if (_insightData!.containsKey('error')) {
      return Text("Error: ${_insightData!['error']}", style: const TextStyle(color: Colors.red));
    }

    // Dynamically render based on the current task type
    List<Widget> contentWidgets = [];
    _insightData!.forEach((key, value) {
      contentWidgets.add(
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                key.replaceAll('_', ' ').toUpperCase(), 
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey)
              ),
              const SizedBox(height: 4),
              Text(value.toString(), style: const TextStyle(fontSize: 16)),
            ],
          ),
        ),
      );
    });

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: contentWidgets,
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      height: MediaQuery.of(context).size.height * 0.5,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Deep Dive: ${widget.targetWord}", style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 16),
          // Tab Row for different AI Tasks
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildTab(LLMTaskType.vocab_fact, "Fun Fact"),
              _buildTab(LLMTaskType.grammar_pill, "Grammar"),
              _buildTab(LLMTaskType.etymology, "Roots"),
            ],
          ),
          const Divider(),
          Expanded(
            child: _isLoading 
                ? const Center(child: CircularProgressIndicator()) 
                : SingleChildScrollView(
                    child: _buildInsightContent(),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildTab(LLMTaskType type, String label) {
    return ActionChip(
      label: Text(label),
      backgroundColor: _currentTask == type ? Colors.blue.shade100 : Colors.grey.shade200,
      onPressed: () => _loadInsight(type),
    );
  }
}

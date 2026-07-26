enum LLMTaskType { cloze, grammar_pill, vocab_fact, etymology, word_association }

extension ParseToString on LLMTaskType {
  String toShortString() {
    return this.toString().split('.').last;
  }
}

class LLMGenerationRequest {
  final String userId;
  final LLMTaskType taskType;
  final String targetWord;
  final String targetLang;
  final String nativeLang;

  LLMGenerationRequest({
    required this.userId,
    required this.taskType,
    required this.targetWord,
    this.targetLang = "Hebrew",
    this.nativeLang = "English",
  });

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'task_type': taskType.toShortString(),
    'target_word': targetWord,
    'target_lang': targetLang,
    'native_lang': nativeLang,
  };
}

class LLMGenerationResponse {
  final String taskType;
  final Map<String, dynamic> content;
  final String modelUsed;

  LLMGenerationResponse.fromJson(Map<String, dynamic> json)
      : taskType = json['task_type'],
        content = Map<String, dynamic>.from(json['content']),
        modelUsed = json['model_used'];
}
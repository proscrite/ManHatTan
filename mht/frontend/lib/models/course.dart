class Course {
  final String id;
  final String learningLanguage;
  final String uiLanguage;

  Course({
    required this.id,
    required this.learningLanguage,
    required this.uiLanguage,
  });

  factory Course.fromJson(Map<String, dynamic> json) {
    return Course(
      id: json['id'],
      learningLanguage: json['learning_language'] ?? 'Unknown',
      uiLanguage: json['ui_language'] ?? 'en',
    );
  }
}
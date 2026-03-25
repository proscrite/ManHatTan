import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'api_client.dart';

class ExerciseService {
  static Future<Map<String, dynamic>?> fetchMultipleChoice(String mode) async {
    final url = Uri.parse('${ApiClient.baseUrl}/exercise/multiple-choice?course_id=${ApiClient.courseId}&mode=$mode');
    try {
      final response = await http.get(url, headers: ApiClient.headers);
      if (response.statusCode == 200) return jsonDecode(response.body);
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> submitMcReview(String vocabId, String userAnswer, String mode) async {
    final url = Uri.parse('${ApiClient.baseUrl}/progress/review/multiple-choice');
    try {
      final response = await http.post(
        url,
        headers: ApiClient.headers,
        body: jsonEncode({
          'vocab_id': vocabId, 'exercise_type': mode, 'user_answer': userAnswer, 'speed': 1.5,
        }),
      );
      if (response.statusCode == 200) return jsonDecode(response.body);
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> fetchWrittenExercise(String mode) async {
    final url = Uri.parse('${ApiClient.baseUrl}/exercise/written?course_id=${ApiClient.courseId}&mode=$mode');
    try {
      final response = await http.get(url, headers: ApiClient.headers);
      if (response.statusCode == 200) return jsonDecode(response.body);
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<bool?> submitWrittenReview(String vocabId, String userAnswer, String mode) async {
    final url = Uri.parse('${ApiClient.baseUrl}/progress/review');
    try {
      final response = await http.post(
        url,
        headers: ApiClient.headers,
        body: jsonEncode({
          'vocab_id': vocabId, 'exercise_type': mode, 'user_answer': userAnswer, 'speed': 2.0,
        }),
      );
      if (response.statusCode == 200) return jsonDecode(response.body)['is_correct'] as bool;
      return null;
    } catch (e) {
      return null;
    }
  }
}
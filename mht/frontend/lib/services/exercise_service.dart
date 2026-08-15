import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'api_client.dart';
// import 'ingestion_service.dart';

class ExerciseService {
  static Future<Map<String, dynamic>?> fetchMultipleChoice(String mode) async {
    final courseId = ApiClient.activeCourse?.id;
    if (courseId == null) throw Exception('No active course selected');

    final url = Uri.parse('${ApiClient.baseUrl}/exercise/multiple-choice?course_id=$courseId&mode=$mode');
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
          'vocab_id': vocabId, 'exercise_type': mode, 'user_answer': userAnswer, 'speed': 1.5, 'grade': 3
        }),
      );
      if (response.statusCode == 200) return jsonDecode(response.body);
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> fetchWrittenExercise(String mode) async {
    
    final courseId = ApiClient.activeCourse?.id;
    final url = Uri.parse('${ApiClient.baseUrl}/exercise/written?course_id=$courseId&mode=$mode');
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
          'vocab_id': vocabId, 'exercise_type': mode, 'user_answer': userAnswer, 'speed': 2.0, 'grade': 3
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return (data['grade'] as int) >= 3;
      }
      return null;
    } catch (e) {
      return null;
    }
  }
  static Future<Map<String, dynamic>?> fetchClozeExercise(String mode) async {
    final courseId = ApiClient.activeCourse?.id;
    if (courseId == null) throw Exception('No active course selected');

    // Route directly to the SRS-aware exercise endpoint
    final url = Uri.parse('${ApiClient.baseUrl}/exercise/cloze?course_id=$courseId&mode=$mode');
    
    try {
      final response = await http.get(
        url,
        headers: ApiClient.headers,
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else if (response.statusCode == 429) {
        throw Exception('RATE_LIMIT');
      } else {
         debugPrint('API Error ${response.statusCode}: ${response.body}');
         return null;
      }
    } catch (e) {
      debugPrint('Exception fetching CLOZE exercise: $e');
      rethrow; // Pass the exception up so the UI can trigger the Rate Limit banner
    }
  }
}
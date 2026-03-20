import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiService {
  // Base URL for the Android Emulator to reach Mac Localhost
  // static const String baseUrl = 'http://10.0.2.2:8000/api/v1'; (for Mac Localhost, only within the computer)

  // Base URL for the Android Emulator to reach Mac Localhost through WiFi
  static const String baseUrl = 'http://192.168.1.225:8000/api/v1';

  // We'll hardcode the course ID for now, but eventually this will come from user login
  static const String courseId = '94955e29-3f26-44a5-837c-6ebcf5b4ec8b';
  // static const String courseId = '3f23e536-b589-487b-bbaa-8c78f0562766';

  // 1. Fetch Vocabulary
  static Future<List<dynamic>> fetchVocabulary() async {
    final url = Uri.parse('$baseUrl/vocabulary/$courseId');
    
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        debugPrint("Server Error: ${response.statusCode}");
        return [];
      }
    } catch (e) {
      debugPrint("Network Error: $e");
      return [];
    }
  }

// Fetch the 4-button question data
  static Future<Map<String, dynamic>?> fetchMultipleChoice(String mode) async {
    // We pass the existing courseId to the backend!
    final url = Uri.parse('$baseUrl/exercise/multiple-choice?course_id=$courseId&mode=$mode');

    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      debugPrint("Fetch Error: ${response.statusCode}");
      return null;
    } catch (e) {
      debugPrint("Network Error: $e");
      return null;
    }
  }

  // Submit the tapped answer
  static Future<Map<String, dynamic>?> submitMcReview(String vocabId, String userAnswer, String mode) async {
    final url = Uri.parse('$baseUrl/progress/review/multiple-choice');

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'vocab_id': vocabId,
          'exercise_type': mode,
          'user_answer': userAnswer,
          'speed': 1.5, // You can calculate actual delta time later
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  // Fetch the Written Exercise
  static Future<Map<String, dynamic>?> fetchWrittenExercise(String mode) async {
    final url = Uri.parse('$baseUrl/exercise/written?course_id=$courseId&mode=$mode');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) return jsonDecode(response.body);
      return null;
    } catch (e) {
      return null;
    }
  }

  // Update your existing submitReview to accept the mode!
  static Future<bool?> submitReview(String vocabId, String userAnswer, String mode) async {
    final url = Uri.parse('$baseUrl/progress/review');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'vocab_id': vocabId,
          'exercise_type': mode, // Passes 'wrt' or 'wdt'
          'user_answer': userAnswer,
          'speed': 2.0, 
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['is_correct'] as bool;
      }
      return null;
    } catch (e) {
      return null;
    }
  }


}
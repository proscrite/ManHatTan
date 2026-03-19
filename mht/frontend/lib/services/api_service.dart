import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiService {
  // Base URL for the Android Emulator to reach Mac Localhost
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
  
  // We'll hardcode the course ID for now, but eventually this will come from user login
  static const String courseId = '3f23e536-b589-487b-bbaa-8c78f0562766';

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

  // 2. Submit Review
  // Now returns a bool? (true = correct, false = incorrect, null = server error)
  static Future<bool?> submitReview(String vocabId, String userAnswer) async {
    final url = Uri.parse('$baseUrl/progress/review');
    
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'vocab_id': vocabId,
          'exercise_type': 'typing_test',
          'user_answer': userAnswer, // Sending the raw text
          'speed': 1.5,
        }),
      );
      
      if (response.statusCode == 200) {
        // Parse the backend's grading decision!
        final data = jsonDecode(response.body);
        return data['is_correct'] as bool;
      } else {
        debugPrint("Server Error: ${response.statusCode}");
        return null;
      }
    } catch (e) {
      debugPrint("Network Error: $e");
      return null;
    }
  }
}
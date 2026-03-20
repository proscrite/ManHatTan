import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  // Base URL for the Android Emulator to reach Mac Localhost
  // static const String baseUrl = 'http://10.0.2.2:8000/api/v1'; (for Mac Localhost, only within the computer)

  // Base URL for the Android Emulator to reach Mac Localhost through WiFi
  static const String baseUrl = 'http://192.168.1.225:8000/api/v1';

  // 1. Initialize Secure Storage and in-memory caches
  static const _storage = FlutterSecureStorage();
  static String? _jwtToken;
  static String? courseId;


  // 2. The Login Method
  static Future<bool> login(String email, String password) async {
    final url = Uri.parse('$baseUrl/auth/login');
    try {
      // FastAPI's OAuth2 expects form-urlencoded, NOT JSON!
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'grant_type': 'password',
          'username': email,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _jwtToken = data['access_token'];
        
        // Save to encrypted storage for future app launches
        await _storage.write(key: 'jwt_token', value: _jwtToken);
        
        // Immediately fetch the user's active course ID
        return await _fetchAndSetCourseId();
      }
      return false;
    } catch (e) {
      debugPrint("Login Error: $e");
      return false;
    }
  }

  // 3. The Auto-Setup Method (Fetches course dynamically)
  static Future<bool> _fetchAndSetCourseId() async {
    final url = Uri.parse('$baseUrl/users/me/courses');
    try {
      final response = await http.get(url, headers: _getAuthHeaders());
      if (response.statusCode == 200) {
        final List<dynamic> courses = jsonDecode(response.body);
        if (courses.isNotEmpty) {
          // Grab the first active course ID
          courseId = courses[0]['id'].toString(); 
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // 4. The Auth Header Helper
  // Use this in ALL your other fetch/submit methods instead of empty headers!
  static Map<String, String> _getAuthHeaders() {
    if (_jwtToken == null) return {'Content-Type': 'application/json'};
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $_jwtToken'
    };
  }

  // 5. Fetch Vocabulary
  static Future<List<dynamic>> fetchVocabulary() async {
    final url = Uri.parse('$baseUrl/vocabulary/$courseId');
    
    try {
      final response = await http.get(url, headers: _getAuthHeaders());
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

  // 6. Fetch the 4-button question data
  static Future<Map<String, dynamic>?> fetchMultipleChoice(String mode) async {
    // We pass the existing courseId to the backend!
    final url = Uri.parse('$baseUrl/exercise/multiple-choice?course_id=$courseId&mode=$mode');

    try {
      final response = await http.get(url, headers: _getAuthHeaders());
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

  // 7. Submit the tapped answer
  static Future<Map<String, dynamic>?> submitMcReview(String vocabId, String userAnswer, String mode) async {
    final url = Uri.parse('$baseUrl/progress/review/multiple-choice');

    try {
      final response = await http.post(
        url,
        headers: _getAuthHeaders(),
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

  // 8. Fetch the Written Exercise
  static Future<Map<String, dynamic>?> fetchWrittenExercise(String mode) async {
    final url = Uri.parse('$baseUrl/exercise/written?course_id=$courseId&mode=$mode');
    try {
      final response = await http.get(url, headers: _getAuthHeaders());
      if (response.statusCode == 200) return jsonDecode(response.body);
      return null;
    } catch (e) {
      return null;
    }
  }

  // 9. Update your existing submitReview to accept the mode!
  static Future<bool?> submitReview(String vocabId, String userAnswer, String mode) async {
    final url = Uri.parse('$baseUrl/progress/review');
    try {
      final response = await http.post(
        url,
        headers: _getAuthHeaders(),
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
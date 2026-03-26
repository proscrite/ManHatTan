import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'api_client.dart';
import 'ingestion_service.dart';

class AuthService {
  static Future<bool> login(String email, String password) async {
    final url = Uri.parse('${ApiClient.baseUrl}/auth/login'); // Or whatever your login route is

    try {
      final response = await http.post(
        url,
        headers: ApiClient.urlEncodedHeaders,
        body: {
          'username': email.trim(), // OAuth2 strictly requires 'username', even if it's an email
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['access_token'];

        // 1. Save the token globally and in secure storage
        ApiClient.jwtToken = token;
        await ApiClient.storage.write(key: 'jwt_token', value: token);

        // 2. Fetch courses (This will return an empty list [] for new users!)
        await IngestionService.fetchMyCourses(); 

        // 3. Return true regardless of whether they have courses yet or not!
        return true; 
      }
      return false; // Wrong password or email
    } catch (e) {
      debugPrint("Login Error: $e");
      return false;
    }
  }

  static Future<bool> _fetchAndSetCourseId() async {
    final url = Uri.parse('${ApiClient.baseUrl}/users/me/courses');
    try {
      final response = await http.get(url, headers: ApiClient.headers);
      if (response.statusCode == 200) {
        final List<dynamic> courses = jsonDecode(response.body);
        if (courses.isNotEmpty) {
          await IngestionService.fetchMyCourses(); // This will set the active course
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  static Future<String?> register(String email, String password) async {
    final url = Uri.parse('${ApiClient.baseUrl}/users');
    
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim(),
          'password': password,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        // Auto-login!
        final loginSuccess = await login(email.trim(), password);
        if (loginSuccess) return null; // Null means no errors!
        return "Account created, but auto-login failed.";
      } else {
        // Try to extract FastAPI's error message (e.g., "Email already registered")
        final errorData = jsonDecode(response.body);
        return errorData['detail'] ?? "Registration failed.";
      }
    } catch (e) {
      debugPrint("Registration Error: $e");
      return "Network error. Please try again.";
    }
  }
}
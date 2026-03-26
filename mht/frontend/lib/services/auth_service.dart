import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'api_client.dart';
import 'ingestion_service.dart';

class AuthService {
  static Future<bool> login(String email, String password) async {
    final url = Uri.parse('${ApiClient.baseUrl}/auth/login');
    try {
      final response = await http.post(
        url,
        headers: ApiClient.urlEncodedHeaders,
        body: {'grant_type': 'password', 'username': email, 'password': password},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        ApiClient.jwtToken = data['access_token'];
        await ApiClient.storage.write(key: 'jwt_token', value: ApiClient.jwtToken);
        return await _fetchAndSetCourseId();
      }
      return false;
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
}
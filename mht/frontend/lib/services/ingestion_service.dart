import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'api_client.dart';
import '../models/course.dart';

class IngestionService {
//   static Course? activeCourse;
//   static List<Course> allCourses = [];  
  
  static Future<List<Course>> fetchMyCourses() async {
    final response = await http.get(
      Uri.parse('${ApiClient.baseUrl}/users/me/courses'),
      headers: ApiClient.headers,
    );

    if (response.statusCode == 200) {
        List<dynamic> data = jsonDecode(response.body);
        ApiClient.allCourses = data.map((json) => Course.fromJson(json)).toList();
        
        // Automatically set the active course if one isn't set yet
        if (ApiClient.allCourses.isNotEmpty && ApiClient.activeCourse == null) {
            ApiClient.activeCourse = ApiClient.allCourses.first;
        }
        
        return ApiClient.allCourses;
    } else {
        throw Exception('Failed to load courses.');
    }

  }

  static Future<Course> createCourse(String learningLang, String uiLang) async {
    final response = await http.post(
        Uri.parse('${ApiClient.baseUrl}/users/me/courses'),
        headers: ApiClient.headers,
        body: jsonEncode({
        'learning_language': learningLang.toLowerCase().trim(),
        'ui_language': uiLang.toLowerCase().trim()
        }),
    );
    
    if (response.statusCode == 200 || response.statusCode == 201) {
        final newCourse = Course.fromJson(jsonDecode(response.body));
        ApiClient.allCourses.add(newCourse);
        ApiClient.activeCourse = newCourse; // Automatically make the new course active
        return newCourse;
    }
    throw Exception('Failed to create course');
    }

  // --- Step 1 of the Wizard ---
  static Future<Map<String, dynamic>> analyzeDocument(File file) async {
    var uri = Uri.parse('${ApiClient.baseUrl}/import/analyze-docs');
    var request = http.MultipartRequest('POST', uri);
    
    if (ApiClient.jwtToken != null) {
      request.headers['Authorization'] = 'Bearer ${ApiClient.jwtToken}';
    }
    
    request.files.add(await http.MultipartFile.fromPath('file', file.path));
    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Analysis failed: ${response.body}');
  }

  // --- Step 2 of the Wizard ---
  static Future<Map<String, dynamic>> uploadDocument(String courseId, File file, {String? targetColor}) async {
    final isCsv = file.path.toLowerCase().endsWith('.csv');
    
    // Dynamically route to /csv or /document
    final endpoint = isCsv ? 'csv' : 'document';
    
    // Build the URL with query parameters
    var urlString = '${ApiClient.baseUrl}/import/$endpoint?course_id=$courseId';
    if (!isCsv && targetColor != null) {
      urlString += '&target_color=$targetColor';
    }
    
    var request = http.MultipartRequest('POST', Uri.parse(urlString));
    if (ApiClient.jwtToken != null) {
      request.headers['Authorization'] = 'Bearer ${ApiClient.jwtToken}';
    }
    request.files.add(await http.MultipartFile.fromPath('file', file.path));

    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception('Upload failed: ${response.body}');
  }
}
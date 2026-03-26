import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'api_client.dart';

class VocabularyService {
  static Future<List<dynamic>> fetchVocabulary() async {
    final url = Uri.parse('${ApiClient.baseUrl}/vocabulary/${ApiClient.activeCourse?.id}');
    try {
      final response = await http.get(url, headers: ApiClient.headers);
      if (response.statusCode == 200) return jsonDecode(response.body);
      return [];
    } catch (e) {
      debugPrint("Network Error: $e");
      return [];
    }
  }
}
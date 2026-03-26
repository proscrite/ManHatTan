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

  static Future<bool> updateWord(String vocabId, String newWordLl, String newWordUl) async {
    final url = Uri.parse('${ApiClient.baseUrl}/vocabulary/$vocabId');
    
    try {
      final response = await http.put(
        url,
        headers: ApiClient.headers,
        body: jsonEncode({
          'word_ll': newWordLl,
          'word_ul': newWordUl,
        }),
      );
      
      return response.statusCode == 200;
    } catch (e) {
      debugPrint("Update Error: $e");
      return false;
    }
  }

  static Future<bool> deleteWord(String vocabId) async {
    final url = Uri.parse('${ApiClient.baseUrl}/vocabulary/$vocabId');
    try {
      final response = await http.delete(url, headers: ApiClient.headers);
      return response.statusCode == 200;
    } catch (e) {
      debugPrint("Delete Error: $e");
      return false;
    }
  }
}
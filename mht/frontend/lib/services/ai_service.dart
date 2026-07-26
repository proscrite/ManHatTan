import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frontend/models/ai_content.dart';
import 'package:frontend/services/api_client.dart'; // Uses your existing auth/routing

class AiService {
  final ApiClient _apiClient = ApiClient();

  Future<LLMGenerationResponse> fetchInsight(LLMGenerationRequest request) async {
    final url = Uri.parse('${ApiClient.baseUrl}/ai/generate');

    final response = await http.post(
      url,
      headers: ApiClient.headers,
      body: json.encode(request.toJson()),
    );
    
    if (response.statusCode == 200) {
      return LLMGenerationResponse.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to generate AI content: ${response.statusCode}');
    }
  }
}
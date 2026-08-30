import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'api_client.dart';
import '../models/chat_turn.dart';

class ChatService {
  static Future<ChatTurnResponse> submitTurn(String userMessage) async {
    final activeCourse = ApiClient.activeCourse;
    if (activeCourse == null) {
      throw Exception('No active course selected.');
    }

    final url = Uri.parse('${ApiClient.baseUrl}/ai/chat');
    final payload = ChatTurnRequest(
      userMessage: userMessage,
      courseId: activeCourse.id,
    );

    try {
      final response = await http.post(
        url,
        headers: ApiClient.headers,
        body: jsonEncode(payload.toJson()),
      );

      if (response.statusCode == 200) {
        return ChatTurnResponse.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Chat API returned status: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('[ChatService] Turn failed: $e');
      rethrow;
    }
  }

  // --- STREAMING PLACEHOLDER ---
  // When upgrading to Phase 5.2 SSE, replace unary POST with an SSE client stream:
  // Stream<String> streamTurn(String userMessage) async* { ... }
}
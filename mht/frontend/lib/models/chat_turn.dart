import 'package:flutter/foundation.dart';

enum MessageSender { user, conversationalist }

class ChatTurnRequest {
  final String userMessage;
  final String courseId;
  final int historyWindow;

  ChatTurnRequest({
    required this.userMessage,
    required this.courseId,
    this.historyWindow = 6,
  });

  Map<String, dynamic> toJson() => {
    'user_message': userMessage,
    'course_id': courseId,
    'history_window': historyWindow,
  };
}

class ChatTurnResponse {
  final String conversationalistMessageLL;
  final String conversationalistMessageUL;
  final String? tutorCritiqueLL;
  final String? tutorCritiqueUL;

  ChatTurnResponse({
    required this.conversationalistMessageLL,
    required this.conversationalistMessageUL,
    this.tutorCritiqueLL,
    this.tutorCritiqueUL,
  });

  factory ChatTurnResponse.fromJson(Map<String, dynamic> json) {
    return ChatTurnResponse(
      conversationalistMessageLL: json['conversationalist_message_ll'] ?? '',
      conversationalistMessageUL: json['conversationalist_message_ul'] ?? '',
      tutorCritiqueLL: json['tutor_critique_ll'],
      tutorCritiqueUL: json['tutor_critique_ul'],
    );
  }
}

class ChatMessageItem {
  final String id;
  final MessageSender sender;
  String messageLL; // Mutable string allows in-place token buffering during streaming
  String? messageUL;
  bool isTranslationVisible;
  final DateTime timestamp;

  ChatMessageItem({
    required this.id,
    required this.sender,
    required this.messageLL,
    this.messageUL,
    this.isTranslationVisible = false,
    required this.timestamp,
  });
}
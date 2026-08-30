// lib/screens/chat_screen.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart' hide TextDirection;
import '../models/chat_turn.dart';
import '../services/api_client.dart';
import '../services/chat_service.dart';
import '../utils/language_helper.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<ChatMessageItem> _messages = [];
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _focusNode = FocusNode();

  bool _isProcessing = false;
  ChatTurnResponse? _currentTutorOverlay;

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _handleSendMessage() async {
    final rawText = _inputController.text.trim();
    if (rawText.isEmpty || _isProcessing) return;

    // 1. Optimistic UI update: Append User Turn
    final userMsg = ChatMessageItem(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sender: MessageSender.user,
      messageLL: rawText,
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(userMsg);
      _isProcessing = true;
    });

    _inputController.clear();
    _scrollToBottom();

    try {
      // 2. Await MAS Graph Response (Turn-Based Unary Call)
      final response = await ChatService.submitTurn(rawText);

      // --- STREAMING PLACEHOLDER ---
      // When implementing SSE streaming:
      // final aiMsg = ChatMessageItem(id: ..., sender: MessageSender.conversationalist, messageLL: '');
      // streamSubscription = ChatService.streamTurn(...).listen((token) { aiMsg.messageLL += token; setState((){}); });

      final aiMsg = ChatMessageItem(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sender: MessageSender.conversationalist,
        messageLL: response.conversationalistMessageLL,
        messageUL: response.conversationalistMessageUL,
        timestamp: DateTime.now(),
      );

      setState(() {
        _messages.add(aiMsg);
        _isProcessing = false;

        // 3. Trigger Tutor Critic Overlay if critique exists
        if (response.tutorCritiqueLL != null && response.tutorCritiqueLL!.isNotEmpty) {
          _currentTutorOverlay = response;
        }
      });

      _scrollToBottom();
    } catch (e) {
      setState(() => _isProcessing = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to generate response: $e'),
            backgroundColor: Colors.red.shade700,
          ),
        );
      }
    }
  }

  void _triggerPanicButton() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('🚨 Profiler adjusted: Simplifying conversational vocabulary.'),
        backgroundColor: Colors.orange,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final activeCourse = ApiClient.activeCourse;
    final learnLang = LanguageHelper.getFlagAndCode(activeCourse?.learningLanguage);

    return Scaffold(
      appBar: AppBar(
        title: Text('$learnLang AI Conversation'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.speed, color: Colors.orangeAccent),
            tooltip: 'Too Complex (Adjust Level)',
            onPressed: _triggerPanicButton,
          ),
        ],
      ),
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                // Dialogue Canvas
                Expanded(
                  child: _messages.isEmpty
                      ? const Center(
                          child: Text(
                            'Start a conversation in your target language!',
                            style: TextStyle(color: Colors.grey),
                          ),
                        )
                      : ListView.builder(
                          controller: _scrollController,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          itemCount: _messages.length,
                          itemBuilder: (context, index) {
                            final msg = _messages[index];
                            return _buildMessageBubble(msg);
                          },
                        ),
                ),

                // Turn-Lock Indicator
                if (_isProcessing)
                  const LinearProgressIndicator(minHeight: 2),

                // Input Dock
                _buildInputDock(),
              ],
            ),

            // Floating Tutor Critique Overlay
            if (_currentTutorOverlay != null)
              _buildTutorCritiqueCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessageItem item) {
    final isUser = item.sender == MessageSender.user;
    final isRtl = Bidi.hasAnyRtl(item.messageLL);

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
        decoration: BoxDecoration(
          color: isUser ? Colors.teal.shade600 : Colors.blueGrey.shade50,
          borderRadius: BorderRadius.circular(16),
          border: isUser ? null : Border.all(color: Colors.blueGrey.shade200),
        ),
        child: Column(
          crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            Directionality(
              textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
              child: Text(
                item.messageLL,
                style: TextStyle(
                  fontSize: 18,
                  color: isUser ? Colors.white : Colors.black87,
                  height: 1.3,
                ),
              ),
            ),
            if (!isUser && item.messageUL != null) ...[
              const SizedBox(height: 6),
              GestureDetector(
                onTap: () {
                  setState(() {
                    item.isTranslationVisible = !item.isTranslationVisible;
                  });
                },
                child: Text(
                  item.isTranslationVisible ? 'Hide translation' : '🌐 Translate',
                  style: TextStyle(fontSize: 12, color: Colors.teal.shade700, fontWeight: FontWeight.bold),
                ),
              ),
              if (item.isTranslationVisible) ...[
                const SizedBox(height: 4),
                Text(
                  item.messageUL!,
                  style: TextStyle(fontSize: 14, color: Colors.grey.shade700, fontStyle: FontStyle.italic),
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTutorCritiqueCard() {
    final overlay = _currentTutorOverlay!;
    final bool isRtl = Bidi.hasAnyRtl(overlay.tutorCritiqueLL ?? '');

    return Positioned(
      bottom: 80,
      left: 16,
      right: 16,
      child: Card(
        color: Colors.amber.shade50,
        elevation: 6,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: BorderSide(color: Colors.amber.shade600, width: 1.5),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  const Icon(Icons.school, color: Colors.amber, size: 22),
                  const SizedBox(width: 8),
                  const Text('Tutor Feedback', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close, size: 18),
                    onPressed: () => setState(() => _currentTutorOverlay = null),
                  ),
                ],
              ),
              if (overlay.tutorCritiqueLL != null) ...[
                const SizedBox(height: 6),
                Directionality(
                  textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
                  child: Text(
                    overlay.tutorCritiqueLL!,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.brown),
                  ),
                ),
              ],
              if (overlay.tutorCritiqueUL != null) ...[
                const SizedBox(height: 4),
                Text(
                  overlay.tutorCritiqueUL!,
                  style: TextStyle(fontSize: 14, color: Colors.brown.shade800),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputDock() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        border: Border(top: BorderSide(color: Colors.grey.shade300)),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _inputController,
              focusNode: _focusNode,
              enabled: !_isProcessing,
              textDirection: TextDirection.ltr, // Auto-adjusted internally via input text
              decoration: InputDecoration(
                hintText: _isProcessing ? 'Agent is replying...' : 'Type a message...',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(24)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
                filled: true,
                fillColor: Colors.grey.shade100,
              ),
              onSubmitted: (_) => _handleSendMessage(),
            ),
          ),
          const SizedBox(width: 8),
          IconButton.filled(
            icon: const Icon(Icons.send),
            style: IconButton.styleFrom(backgroundColor: Colors.teal.shade600),
            onPressed: _isProcessing ? null : _handleSendMessage,
          ),
        ],
      ),
    );
  }
}
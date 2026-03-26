import 'package:flutter/material.dart';

class SmartGuardrailCard extends StatelessWidget {
  final String targetLang;
  final String activeLang;
  final String? backgroundMatchLang; // Null if no match exists
  final VoidCallback onSwitchCourse;
  final VoidCallback onCreateCourse;

  const SmartGuardrailCard({
    super.key,
    required this.targetLang,
    required this.activeLang,
    this.backgroundMatchLang,
    required this.onSwitchCourse,
    required this.onCreateCourse,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 16, bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.shade50, 
        borderRadius: BorderRadius.circular(12), 
        border: Border.all(color: Colors.orange.shade300)
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              const Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 28),
              const SizedBox(width: 12),
              Expanded(child: Text(
                'Language Mismatch: Document is [${targetLang.toUpperCase()}], but Active Course is [${activeLang.toUpperCase()}].',
                style: TextStyle(color: Colors.orange.shade900, fontWeight: FontWeight.bold),
              )),
            ],
          ),
          const SizedBox(height: 16),
          
          if (backgroundMatchLang != null)
            ElevatedButton.icon(
              icon: const Icon(Icons.swap_horiz),
              label: Text('Switch to ${backgroundMatchLang!.toUpperCase()} Course'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.orange.shade600, foregroundColor: Colors.white),
              onPressed: onSwitchCourse,
            )
          else
            ElevatedButton.icon(
              icon: const Icon(Icons.add),
              label: Text('Create ${targetLang.toUpperCase()} Course'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.orange.shade600, foregroundColor: Colors.white),
              onPressed: onCreateCourse,
            ),
        ],
      ),
    );
  }
}


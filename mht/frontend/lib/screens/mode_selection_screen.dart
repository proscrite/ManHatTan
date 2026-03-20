import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'multiple_choice_screen.dart';
import 'written_input_screen.dart';

class ModeSelectionScreen extends StatelessWidget {
  const ModeSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Manhattan Hub'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Choose Your Exercise',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 48),

              // Mode 1: The Original Dashboard (Typing)
              _buildModeCard(
                context,
                title: 'Vocabulary Dashboard',
                subtitle: 'Review your list and practice exact typing.',
                icon: Icons.list_alt,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const DashboardScreen()),
                  );
                },
              ),

              const SizedBox(height: 20),

              // Mode 2: MARTE exercise
              _buildModeCard(
                context,
                title: 'Multiple Choice Reversed Translation',
                subtitle: 'Fast-paced 4-button flashcard drills.',
                icon: Icons.grid_view,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const MultipleChoiceScreen(mode: 'mrt',)),
                  );
                },
              ),

              // Mode 3: MADTE exercise
              _buildModeCard(
                context,
                title: 'Multiple Choice Direct Translation',
                subtitle: 'Fast-paced 4-button flashcard drills.',
                icon: Icons.grid_view,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const MultipleChoiceScreen(mode: 'mdt',)),
                  );
                },
              ),

              // Mode 4: WIDTE exercise
              _buildModeCard(
                context,
                title: 'Written Input',
                subtitle: 'Type the translation in the target language.',
                icon: Icons.edit,

                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const WrittenInputScreen(mode: 'wdt',)),
                  );
                },
              ),

              // Mode 5: WIRTE exercise
              _buildModeCard(
                context,
                title: 'Written Input Reversed Translation',
                subtitle: 'Type the translation in the target language.',
                icon: Icons.edit,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const WrittenInputScreen(mode: 'wt',)),
                  );
                },
              )


            ],
          ),
        ),
      ),
    );
  }

  // A reusable builder for our mode selection cards
  Widget _buildModeCard(
      BuildContext context, {
        required String title,
        required String subtitle,
        required IconData icon,
        required VoidCallback onTap,
      }) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Row(
            children: [
              Icon(icon, size: 40, color: Colors.teal),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 6),
                    Text(subtitle, style: TextStyle(fontSize: 14, color: Colors.grey[600])),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward_ios, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }
}
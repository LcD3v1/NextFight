import 'package:flutter/material.dart';

class FoundationPage extends StatelessWidget {
  const FoundationPage({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('NextFight')),
    body: const SafeArea(
      child: Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Text(
            'Foundation ready',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
            textAlign: TextAlign.center,
          ),
        ),
      ),
    ),
  );
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/features/auth/application/auth_controller.dart';
import 'package:nextfight/features/auth/presentation/auth_page.dart';
import 'package:nextfight/features/home/presentation/home_page.dart';

class SessionGatePage extends ConsumerWidget {
  const SessionGatePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(authControllerProvider);
    return session.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (_, _) => const AuthPage(),
      data: (value) => value == null ? const AuthPage() : const HomePage(),
    );
  }
}

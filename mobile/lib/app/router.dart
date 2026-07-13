import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:nextfight/features/auth/presentation/password_recovery_pages.dart';
import 'package:nextfight/features/auth/presentation/session_gate_page.dart';
import 'package:nextfight/features/events/presentation/event_detail_page.dart';
import 'package:nextfight/features/fights/presentation/fight_detail_page.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    routes: [
      GoRoute(path: '/', builder: (_, _) => const SessionGatePage()),
      GoRoute(
        path: '/forgot-password',
        builder: (_, _) => const ForgotPasswordPage(),
      ),
      GoRoute(
        path: '/reset-password',
        builder: (_, state) => ResetPasswordPage(
          initialToken: state.uri.queryParameters['token'] ?? '',
        ),
      ),
      GoRoute(
        path: '/events/:eventId',
        builder: (_, state) =>
            EventDetailPage(eventId: state.pathParameters['eventId']!),
      ),
      GoRoute(
        path: '/fights/:fightId',
        builder: (_, state) => FightDetailPage(
          fightId: state.pathParameters['fightId']!,
        ),
      ),
    ],
  );
  ref.onDispose(router.dispose);
  return router;
});

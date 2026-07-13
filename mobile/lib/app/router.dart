import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:nextfight/features/auth/presentation/session_gate_page.dart';
import 'package:nextfight/features/events/presentation/event_detail_page.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    routes: [
      GoRoute(path: '/', builder: (_, _) => const SessionGatePage()),
      GoRoute(
        path: '/events/:eventId',
        builder: (_, state) =>
            EventDetailPage(eventId: state.pathParameters['eventId']!),
      ),
    ],
  );
  ref.onDispose(router.dispose);
  return router;
});

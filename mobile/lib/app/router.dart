import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:nextfight/features/foundation/presentation/foundation_page.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    routes: [GoRoute(path: '/', builder: (_, _) => const FoundationPage())],
  );
  ref.onDispose(router.dispose);
  return router;
});

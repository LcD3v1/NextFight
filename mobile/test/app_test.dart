import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nextfight/app/app.dart';
import 'package:nextfight/app/configuration.dart';
import 'package:nextfight/features/auth/data/session_storage.dart';
import 'package:nextfight/features/auth/domain/auth_session.dart';

class EmptySessionStorage implements SessionStorage {
  @override
  Future<void> clear() async {}

  @override
  Future<AuthSession?> read() async => null;

  @override
  Future<void> save(AuthSession session) async {}
}

void main() {
  testWidgets('shows sign in for a visitor without a session', (tester) async {
    final configuration = AppConfiguration(
      environment: AppEnvironment.local,
      apiBaseUrl: Uri.parse('http://localhost:8000/api/v1'),
    );
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          appConfigurationProvider.overrideWithValue(configuration),
          sessionStorageProvider.overrideWithValue(EmptySessionStorage()),
        ],
        child: const NextFightApp(),
      ),
    );
    await tester.pump();
    await tester.pump();

    expect(find.text('NextFight'), findsOneWidget);
    expect(find.text('Sign in'), findsWidgets);
    expect(find.text('Foundation ready'), findsNothing);
  });
}

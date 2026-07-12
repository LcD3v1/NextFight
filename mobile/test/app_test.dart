import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nextfight/app/app.dart';
import 'package:nextfight/app/configuration.dart';

void main() {
  testWidgets('renders the application foundation', (tester) async {
    final configuration = AppConfiguration(
      environment: AppEnvironment.local,
      apiBaseUrl: Uri.parse('http://localhost:8000/api/v1'),
    );
    await tester.pumpWidget(
      ProviderScope(
        overrides: [appConfigurationProvider.overrideWithValue(configuration)],
        child: const NextFightApp(),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Foundation ready'), findsOneWidget);
  });
}

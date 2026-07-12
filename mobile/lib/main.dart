import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/app/app.dart';
import 'package:nextfight/app/configuration.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final configuration = AppConfiguration.fromEnvironment();
  runApp(
    ProviderScope(
      overrides: [appConfigurationProvider.overrideWithValue(configuration)],
      child: const NextFightApp(),
    ),
  );
}

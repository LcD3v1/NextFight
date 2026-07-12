import 'package:flutter_riverpod/flutter_riverpod.dart';

enum AppEnvironment { local, development, staging, production }

class AppConfiguration {
  const AppConfiguration({required this.environment, required this.apiBaseUrl});

  factory AppConfiguration.fromEnvironment() {
    const environment = String.fromEnvironment(
      'APP_ENV',
      defaultValue: 'local',
    );
    const apiUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://localhost:8000/api/v1',
    );
    return AppConfiguration(
      environment: AppEnvironment.values.byName(environment),
      apiBaseUrl: Uri.parse(apiUrl),
    );
  }

  final AppEnvironment environment;
  final Uri apiBaseUrl;
}

final appConfigurationProvider = Provider<AppConfiguration>(
  (ref) => throw StateError('AppConfiguration was not provided.'),
);

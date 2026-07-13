import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/app/locale_controller.dart';
import 'package:nextfight/features/auth/application/auth_controller.dart';
import 'package:nextfight/l10n/app_localizations.dart';

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = AppLocalizations.of(context);
    final session = ref.watch(authControllerProvider).value;
    return Scaffold(
      appBar: AppBar(title: Text(strings.profile)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          CircleAvatar(
            radius: 36,
            child: Text(
              session?.user.displayName.characters.first.toUpperCase() ?? 'N',
            ),
          ),
          const SizedBox(height: 12),
          Center(
            child: Text(
              session?.user.displayName ?? '',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          Center(child: Text(session?.user.email ?? '')),
          const SizedBox(height: 32),
          Text(
            strings.language,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          RadioGroup<String>(
            groupValue: Localizations.localeOf(context).languageCode,
            onChanged: (value) {
              if (value != null) {
                ref.read(localeProvider.notifier).select(value);
              }
            },
            child: Column(
              children: [
                RadioListTile(value: 'pt', title: Text(strings.portuguese)),
                RadioListTile(value: 'en', title: Text(strings.english)),
              ],
            ),
          ),
          const SizedBox(height: 24),
          OutlinedButton.icon(
            onPressed: () => ref.read(authControllerProvider.notifier).logout(),
            icon: const Icon(Icons.logout),
            label: Text(strings.signOut),
          ),
        ],
      ),
    );
  }
}

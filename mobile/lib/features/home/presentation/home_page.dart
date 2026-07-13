import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/features/engagement/presentation/alerts_page.dart';
import 'package:nextfight/features/engagement/presentation/favorites_page.dart';
import 'package:nextfight/features/events/presentation/events_page.dart';
import 'package:nextfight/features/notifications/application/push_registration_controller.dart';
import 'package:nextfight/features/profile/presentation/profile_page.dart';
import 'package:nextfight/l10n/app_localizations.dart';

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    ref.watch(pushRegistrationProvider);
    final strings = AppLocalizations.of(context);
    return Scaffold(
      body: IndexedStack(
        index: _index,
        children: const [
          EventsPage(),
          FavoritesPage(),
          AlertsPage(),
          ProfilePage(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (value) => setState(() => _index = value),
        destinations: [
          NavigationDestination(
            icon: const Icon(Icons.sports_mma),
            label: strings.events,
          ),
          NavigationDestination(
            icon: const Icon(Icons.favorite_outline),
            label: strings.favorites,
          ),
          NavigationDestination(
            icon: const Icon(Icons.notifications_outlined),
            label: strings.alerts,
          ),
          NavigationDestination(
            icon: const Icon(Icons.person_outline),
            label: strings.profile,
          ),
        ],
      ),
    );
  }
}

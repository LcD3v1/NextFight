import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/features/engagement/data/engagement_repository.dart';
import 'package:nextfight/features/events/data/events_repository.dart';
import 'package:nextfight/features/events/domain/event.dart';
import 'package:nextfight/l10n/app_localizations.dart';

class FightDetailPage extends ConsumerWidget {
  const FightDetailPage({required this.fightId, super.key});

  final String fightId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fight = ref.watch(fightProvider(fightId));
    return Scaffold(
      appBar: AppBar(title: Text(AppLocalizations.of(context).fightCard)),
      body: fight.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: TextButton(
            onPressed: () => ref.invalidate(fightProvider(fightId)),
            child: Text(AppLocalizations.of(context).retry),
          ),
        ),
        data: (item) => _FightContent(fight: item),
      ),
    );
  }
}

class _FightContent extends ConsumerWidget {
  const _FightContent({required this.fight});

  final Fight fight;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = AppLocalizations.of(context);
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Text(
          fight.status.toUpperCase(),
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.labelLarge,
        ),
        const SizedBox(height: 24),
        Row(
          children: [
            Expanded(child: _Athlete(name: fight.redAthlete.name)),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text(strings.versus),
            ),
            Expanded(child: _Athlete(name: fight.blueAthlete.name)),
          ],
        ),
        const SizedBox(height: 24),
        if (fight.weightClass != null)
          Center(child: Text(fight.weightClass!)),
        Center(child: Text('${fight.roundsScheduled} rounds')),
        const SizedBox(height: 32),
        FilledButton.icon(
          onPressed: () async {
            await ref.read(engagementRepositoryProvider).createAlert(
              fightId: fight.id,
              triggerType: 'next_fight',
            );
            ref.invalidate(alertsProvider);
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(strings.alertCreated)),
              );
            }
          },
          icon: const Icon(Icons.add_alert),
          label: Text(strings.createAlert),
        ),
      ],
    );
  }
}

class _Athlete extends StatelessWidget {
  const _Athlete({required this.name});

  final String name;

  @override
  Widget build(BuildContext context) => Column(
    children: [
      const CircleAvatar(radius: 42, child: Icon(Icons.person, size: 42)),
      const SizedBox(height: 12),
      Text(name, textAlign: TextAlign.center),
    ],
  );
}

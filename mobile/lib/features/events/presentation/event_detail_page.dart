import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:nextfight/features/engagement/data/engagement_repository.dart';
import 'package:nextfight/features/events/data/events_repository.dart';
import 'package:nextfight/features/events/domain/event.dart';
import 'package:nextfight/features/realtime/data/realtime_client.dart';
import 'package:nextfight/l10n/app_localizations.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class EventDetailPage extends ConsumerWidget {
  const EventDetailPage({required this.eventId, super.key});

  final String eventId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final event = ref.watch(eventProvider(eventId));
    return Scaffold(
      appBar: AppBar(title: const Text('NextFight')),
      body: event.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: FilledButton(
            onPressed: () => ref.invalidate(eventProvider(eventId)),
            child: Text(AppLocalizations.of(context).retry),
          ),
        ),
        data: (item) => _EventContent(event: item),
      ),
    );
  }
}

class _EventContent extends ConsumerWidget {
  const _EventContent({required this.event});

  final FightEvent event;

  Future<void> _favorite(BuildContext context, WidgetRef ref) async {
    await ref.read(engagementRepositoryProvider).addFavorite(event.id);
    ref.invalidate(favoritesProvider);
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context).favoriteAdded)),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = AppLocalizations.of(context);
    final locale = Localizations.localeOf(context).toLanguageTag();
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (event.isLive) _LiveEventConnection(eventId: event.id),
        Text(
          event.organization.name,
          style: Theme.of(context).textTheme.labelLarge,
        ),
        const SizedBox(height: 8),
        Text(event.name, style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 8),
        Text(
          DateFormat.yMMMMd(
            locale,
          ).add_Hm().format(event.scheduledStartAt.toLocal()),
        ),
        const SizedBox(height: 16),
        OutlinedButton.icon(
          onPressed: () => _favorite(context, ref),
          icon: const Icon(Icons.favorite_outline),
          label: Text(strings.favorites),
        ),
        const SizedBox(height: 24),
        Text(strings.fightCard, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        for (final fight in event.fights) _FightTile(fight: fight),
      ],
    );
  }
}

class _FightTile extends ConsumerWidget {
  const _FightTile({required this.fight});

  final Fight fight;

  Future<void> _alert(BuildContext context, WidgetRef ref) async {
    await ref
        .read(engagementRepositoryProvider)
        .createAlert(fightId: fight.id, triggerType: 'next_fight');
    ref.invalidate(alertsProvider);
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context).alertCreated)),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) => Card(
    child: ListTile(
      contentPadding: const EdgeInsets.all(14),
      title: Text('${fight.redAthlete.name}  vs  ${fight.blueAthlete.name}'),
      subtitle: Text(
        [fight.weightClass, fight.status].whereType<String>().join(' • '),
      ),
      trailing: IconButton(
        tooltip: AppLocalizations.of(context).createAlert,
        onPressed: () => _alert(context, ref),
        icon: const Icon(Icons.add_alert_outlined),
      ),
    ),
  );
}

class _LiveEventConnection extends ConsumerStatefulWidget {
  const _LiveEventConnection({required this.eventId});

  final String eventId;

  @override
  ConsumerState<_LiveEventConnection> createState() =>
      _LiveEventConnectionState();
}

class _LiveEventConnectionState extends ConsumerState<_LiveEventConnection> {
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;

  @override
  void initState() {
    super.initState();
    unawaited(_connect());
  }

  Future<void> _connect() async {
    try {
      _channel = await ref
          .read(realtimeClientProvider)
          .connectToEvent(widget.eventId);
      _subscription = _channel?.stream.listen(
        (_) => ref.invalidate(eventProvider(widget.eventId)),
      );
    } on Object {
      // The regular API remains the source of truth if realtime is unavailable.
    }
  }

  @override
  void dispose() {
    unawaited(_subscription?.cancel());
    unawaited(_channel?.sink.close());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Align(
      alignment: Alignment.centerLeft,
      child: Chip(
        avatar: const Icon(Icons.circle, size: 12),
        label: Text(AppLocalizations.of(context).live),
      ),
    ),
  );
}

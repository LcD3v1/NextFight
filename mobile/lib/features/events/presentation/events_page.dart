import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:nextfight/features/events/data/events_repository.dart';
import 'package:nextfight/features/events/domain/event.dart';
import 'package:nextfight/l10n/app_localizations.dart';

class EventsPage extends ConsumerWidget {
  const EventsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = AppLocalizations.of(context);
    final events = ref.watch(eventsProvider);
    return Scaffold(
      appBar: AppBar(title: Text(strings.upcomingEvents)),
      body: RefreshIndicator(
        onRefresh: () => ref.refresh(eventsProvider.future),
        child: events.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, _) => _MessageList(
            message: strings.genericError,
            action: () => ref.invalidate(eventsProvider),
          ),
          data: (items) => items.isEmpty
              ? _MessageList(message: strings.noEvents)
              : ListView.separated(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                  itemCount: items.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 12),
                  itemBuilder: (_, index) => _EventCard(event: items[index]),
                ),
        ),
      ),
    );
  }
}

class _EventCard extends StatelessWidget {
  const _EventCard({required this.event});

  final FightEvent event;

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).toLanguageTag();
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => context.push('/events/${event.id}'),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(child: Text(event.organization.name.toUpperCase())),
                  if (event.isLive) const Chip(label: Text('LIVE')),
                ],
              ),
              const SizedBox(height: 10),
              Text(event.name, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              Text(
                DateFormat.yMMMd(
                  locale,
                ).add_Hm().format(event.scheduledStartAt.toLocal()),
              ),
              if (event.city != null) Text(event.city!),
            ],
          ),
        ),
      ),
    );
  }
}

class _MessageList extends StatelessWidget {
  const _MessageList({required this.message, this.action});

  final String message;
  final VoidCallback? action;

  @override
  Widget build(BuildContext context) => ListView(
    physics: const AlwaysScrollableScrollPhysics(),
    children: [
      const SizedBox(height: 180),
      Icon(
        Icons.sports_mma,
        size: 48,
        color: Theme.of(context).colorScheme.outline,
      ),
      const SizedBox(height: 16),
      Center(child: Text(message)),
      if (action != null)
        Center(
          child: TextButton(
            onPressed: action,
            child: Text(AppLocalizations.of(context).retry),
          ),
        ),
    ],
  );
}

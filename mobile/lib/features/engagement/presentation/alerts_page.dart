import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/features/engagement/data/engagement_repository.dart';
import 'package:nextfight/l10n/app_localizations.dart';

class AlertsPage extends ConsumerWidget {
  const AlertsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = AppLocalizations.of(context);
    final alerts = ref.watch(alertsProvider);
    return Scaffold(
      appBar: AppBar(title: Text(strings.alerts)),
      body: alerts.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: TextButton(
            onPressed: () => ref.invalidate(alertsProvider),
            child: Text(strings.retry),
          ),
        ),
        data: (items) => items.isEmpty
            ? Center(child: Text(strings.noAlerts))
            : RefreshIndicator(
                onRefresh: () => ref.refresh(alertsProvider.future),
                child: ListView.separated(
                  itemCount: items.length,
                  separatorBuilder: (_, _) => const Divider(height: 1),
                  itemBuilder: (_, index) {
                    final item = items[index];
                    return ListTile(
                      leading: const Icon(Icons.notifications_active_outlined),
                      title: Text(item.triggerType.replaceAll('_', ' ')),
                      subtitle: Text(item.status),
                      trailing: IconButton(
                        tooltip: strings.remove,
                        onPressed: () async {
                          await ref
                              .read(engagementRepositoryProvider)
                              .deleteAlert(item.id);
                          ref.invalidate(alertsProvider);
                        },
                        icon: const Icon(Icons.delete_outline),
                      ),
                    );
                  },
                ),
              ),
      ),
    );
  }
}

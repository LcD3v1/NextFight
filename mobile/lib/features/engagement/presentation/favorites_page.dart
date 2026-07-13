import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/features/engagement/data/engagement_repository.dart';
import 'package:nextfight/l10n/app_localizations.dart';

class FavoritesPage extends ConsumerWidget {
  const FavoritesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final strings = AppLocalizations.of(context);
    final favorites = ref.watch(favoritesProvider);
    return Scaffold(
      appBar: AppBar(title: Text(strings.favorites)),
      body: favorites.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: TextButton(
            onPressed: () => ref.invalidate(favoritesProvider),
            child: Text(strings.retry),
          ),
        ),
        data: (items) => items.isEmpty
            ? Center(child: Text(strings.noFavorites))
            : RefreshIndicator(
                onRefresh: () => ref.refresh(favoritesProvider.future),
                child: ListView.builder(
                  itemCount: items.length,
                  itemBuilder: (_, index) {
                    final item = items[index];
                    return ListTile(
                      leading: const Icon(Icons.favorite),
                      title: Text(item.targetType),
                      subtitle: Text(item.targetId),
                      trailing: IconButton(
                        tooltip: strings.remove,
                        onPressed: () async {
                          await ref
                              .read(engagementRepositoryProvider)
                              .removeFavorite(item.id);
                          ref.invalidate(favoritesProvider);
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

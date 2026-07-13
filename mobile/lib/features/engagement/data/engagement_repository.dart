import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/core/network/dio_provider.dart';
import 'package:nextfight/features/engagement/domain/engagement.dart';

class EngagementRepository {
  const EngagementRepository(this._dio);

  final Dio _dio;

  Future<List<Favorite>> listFavorites() async =>
      _list<Favorite>('/me/favorites', Favorite.fromJson);

  Future<Favorite> addFavorite(String eventId) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/me/favorites',
      data: {'target_type': 'event', 'target_id': eventId},
    );
    return Favorite.fromJson(response.data!);
  }

  Future<void> removeFavorite(String favoriteId) =>
      _dio.delete<void>('/me/favorites/$favoriteId');

  Future<List<FightAlert>> listAlerts() =>
      _list<FightAlert>('/me/alerts', FightAlert.fromJson);

  Future<FightAlert> createAlert({
    required String fightId,
    required String triggerType,
    int? leadMinutes,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/me/alerts',
      data: {
        'fight_id': fightId,
        'trigger_type': triggerType,
        'lead_minutes': ?leadMinutes,
      },
    );
    return FightAlert.fromJson(response.data!);
  }

  Future<void> deleteAlert(String alertId) =>
      _dio.delete<void>('/me/alerts/$alertId');

  Future<List<T>> _list<T>(
    String path,
    T Function(Map<String, dynamic>) parser,
  ) async {
    final response = await _dio.get<List<dynamic>>(path);
    return response.data!
        .map((item) => parser(item as Map<String, dynamic>))
        .toList(growable: false);
  }
}

final engagementRepositoryProvider = Provider<EngagementRepository>(
  (ref) => EngagementRepository(ref.watch(dioProvider)),
);

final favoritesProvider = FutureProvider<List<Favorite>>(
  (ref) => ref.watch(engagementRepositoryProvider).listFavorites(),
);

final alertsProvider = FutureProvider<List<FightAlert>>(
  (ref) => ref.watch(engagementRepositoryProvider).listAlerts(),
);

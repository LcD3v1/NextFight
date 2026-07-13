import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/core/network/dio_provider.dart';
import 'package:nextfight/features/events/domain/event.dart';

class EventsRepository {
  const EventsRepository(this._dio);

  final Dio _dio;

  Future<List<FightEvent>> listEvents() async {
    final response = await _dio.get<Map<String, dynamic>>('/events');
    final items = response.data!['items'] as List<dynamic>;
    return items
        .map((item) => FightEvent.fromJson(item as Map<String, dynamic>))
        .toList(growable: false);
  }

  Future<FightEvent> getEvent(String eventId) async {
    final response = await _dio.get<Map<String, dynamic>>('/events/$eventId');
    return FightEvent.fromJson(response.data!);
  }
}

final eventsRepositoryProvider = Provider<EventsRepository>(
  (ref) => EventsRepository(ref.watch(dioProvider)),
);

final eventsProvider = FutureProvider<List<FightEvent>>(
  (ref) => ref.watch(eventsRepositoryProvider).listEvents(),
);

final eventProvider = FutureProvider.family<FightEvent, String>(
  (ref, eventId) => ref.watch(eventsRepositoryProvider).getEvent(eventId),
);

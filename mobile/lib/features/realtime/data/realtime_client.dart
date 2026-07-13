import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/app/configuration.dart';
import 'package:nextfight/features/auth/data/session_storage.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class RealtimeClient {
  const RealtimeClient(this._configuration, this._storage);

  final AppConfiguration _configuration;
  final SessionStorage _storage;

  Future<WebSocketChannel?> connectToEvent(String eventId) async {
    final session = await _storage.read();
    if (session == null) return null;
    final apiUri = _configuration.apiBaseUrl;
    final socketUri = apiUri.replace(
      scheme: apiUri.scheme == 'https' ? 'wss' : 'ws',
      path: '/ws',
      query: null,
    );
    final channel = WebSocketChannel.connect(socketUri);
    await channel.ready;
    channel.sink.add(
      jsonEncode({
        'type': 'authenticate',
        'access_token': session.accessToken,
        'topics': ['event.$eventId'],
      }),
    );
    return channel;
  }
}

final realtimeClientProvider = Provider<RealtimeClient>(
  (ref) => RealtimeClient(
    ref.watch(appConfigurationProvider),
    ref.watch(sessionStorageProvider),
  ),
);

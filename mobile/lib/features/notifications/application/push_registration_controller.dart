import 'dart:async';

import 'package:dio/dio.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/core/network/dio_provider.dart';
import 'package:nextfight/features/auth/application/auth_controller.dart';

class PushRegistrationController extends AsyncNotifier<void> {
  StreamSubscription<String>? _tokenSubscription;

  @override
  Future<void> build() async {
    ref.onDispose(() => _tokenSubscription?.cancel());
    final session = ref.watch(authControllerProvider).value;
    if (session == null || kIsWeb || !_isMobilePlatform) return;

    try {
      if (Firebase.apps.isEmpty) await Firebase.initializeApp();
      final messaging = FirebaseMessaging.instance;
      final settings = await messaging.requestPermission(provisional: true);
      if (settings.authorizationStatus == AuthorizationStatus.denied) return;
      final token = await messaging.getToken();
      if (token != null) await _register(token);
      _tokenSubscription = messaging.onTokenRefresh.listen(_register);
    } on FirebaseException {
      // Local builds may intentionally omit provider configuration.
    }
  }

  bool get _isMobilePlatform =>
      defaultTargetPlatform == TargetPlatform.android ||
      defaultTargetPlatform == TargetPlatform.iOS;

  Future<void> _register(String token) async {
    try {
      await ref.read(dioProvider).post<void>(
        '/me/devices',
        data: {
          'platform': defaultTargetPlatform == TargetPlatform.iOS
              ? 'ios'
              : 'android',
          'push_token': token,
          'app_version': '1.0.0',
          'notifications_enabled': true,
        },
      );
    } on DioException {
      // Token refresh will retry naturally; app usage must remain available.
    }
  }
}

final pushRegistrationProvider =
    AsyncNotifierProvider<PushRegistrationController, void>(
      PushRegistrationController.new,
    );

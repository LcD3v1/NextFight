import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:nextfight/features/auth/domain/auth_session.dart';

abstract interface class SessionStorage {
  Future<AuthSession?> read();
  Future<void> save(AuthSession session);
  Future<void> clear();
}

class SecureSessionStorage implements SessionStorage {
  const SecureSessionStorage(this._storage);
  static const _key = 'nextfight.auth.session';
  final FlutterSecureStorage _storage;

  @override
  Future<AuthSession?> read() async {
    final value = await _storage.read(key: _key);
    if (value == null) return null;
    try {
      return AuthSession.fromJson(jsonDecode(value) as Map<String, dynamic>);
    } on Object {
      await clear();
      return null;
    }
  }

  @override
  Future<void> save(AuthSession session) =>
      _storage.write(key: _key, value: jsonEncode(session.toJson()));

  @override
  Future<void> clear() => _storage.delete(key: _key);
}

final sessionStorageProvider = Provider<SessionStorage>(
  (ref) => const SecureSessionStorage(FlutterSecureStorage()),
);

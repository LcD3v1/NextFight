import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/features/auth/data/auth_repository.dart';
import 'package:nextfight/features/auth/data/session_storage.dart';
import 'package:nextfight/features/auth/domain/auth_session.dart';

class AuthController extends AsyncNotifier<AuthSession?> {
  @override
  Future<AuthSession?> build() => ref.watch(sessionStorageProvider).read();

  Future<void> login({required String email, required String password}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final session = await ref
          .read(authRepositoryProvider)
          .login(email: email.trim(), password: password);
      await ref.read(sessionStorageProvider).save(session);
      return session;
    });
  }

  Future<void> register({
    required String email,
    required String password,
    required String displayName,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final session = await ref
          .read(authRepositoryProvider)
          .register(
            email: email.trim(),
            password: password,
            displayName: displayName.trim(),
          );
      await ref.read(sessionStorageProvider).save(session);
      return session;
    });
  }

  Future<void> logout() async {
    final current = state.value;
    await ref.read(sessionStorageProvider).clear();
    state = const AsyncData(null);
    if (current != null) {
      try {
        await ref.read(authRepositoryProvider).logout(current.refreshToken);
      } on DioException {
        // Local credentials are already removed; remote revocation is best effort.
      }
    }
  }

  Future<void> updateProfile({
    String? displayName,
    String? locale,
    String? timezone,
  }) async {
    final current = state.value;
    if (current == null) return;
    final user = await ref.read(authRepositoryProvider).updateProfile(
      displayName: displayName,
      locale: locale,
      timezone: timezone,
    );
    final updated = current.withUser(user);
    await ref.read(sessionStorageProvider).save(updated);
    state = AsyncData(updated);
  }
}

final authControllerProvider =
    AsyncNotifierProvider<AuthController, AuthSession?>(AuthController.new);

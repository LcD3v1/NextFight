import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/core/network/dio_provider.dart';
import 'package:nextfight/features/auth/domain/auth_session.dart';

class AuthRepository {
  const AuthRepository(this._dio);

  final Dio _dio;

  Future<AuthSession> login({
    required String email,
    required String password,
  }) async => AuthSession.fromJson(
    (await _dio.post<Map<String, dynamic>>(
      '/auth/login',
      data: {'email': email, 'password': password},
    )).data!,
  );

  Future<AuthSession> register({
    required String email,
    required String password,
    required String displayName,
  }) async => AuthSession.fromJson(
    (await _dio.post<Map<String, dynamic>>(
      '/auth/register',
      data: {'email': email, 'password': password, 'display_name': displayName},
    )).data!,
  );

  Future<void> logout(String refreshToken) =>
      _dio.post<void>('/auth/logout', data: {'refresh_token': refreshToken});
}

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(ref.watch(dioProvider)),
);

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

  Future<AuthUser> updateProfile({
    String? displayName,
    String? locale,
    String? timezone,
  }) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/me',
      data: {
        'display_name': ?displayName,
        'locale': ?locale,
        'timezone': ?timezone,
      },
    );
    return AuthUser.fromJson(response.data!);
  }

  Future<String?> forgotPassword(String email) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/forgot-password',
      data: {'email': email.trim()},
    );
    return response.data!['reset_token'] as String?;
  }

  Future<void> resetPassword({
    required String token,
    required String password,
  }) => _dio.post<void>(
    '/auth/reset-password',
    data: {'token': token.trim(), 'password': password},
  );
}

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(ref.watch(dioProvider)),
);

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/app/configuration.dart';
import 'package:nextfight/features/auth/data/session_storage.dart';
import 'package:nextfight/features/auth/domain/auth_session.dart';

final dioProvider = Provider<Dio>((ref) {
  final configuration = ref.watch(appConfigurationProvider);
  final options = BaseOptions(
    baseUrl: configuration.apiBaseUrl.toString(),
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 15),
    responseType: ResponseType.json,
  );
  final dio = Dio(options);
  final refreshDio = Dio(options);
  final storage = ref.read(sessionStorageProvider);
  Future<void>? refreshOperation;

  Future<void> refreshSession() async {
    final session = await storage.read();
    if (session == null) throw StateError('No session available to refresh.');
    final response = await refreshDio.post<Map<String, dynamic>>(
      '/auth/refresh',
      data: {'refresh_token': session.refreshToken},
    );
    await storage.save(AuthSession.fromJson(response.data!));
  }

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (request, handler) async {
        final session = await storage.read();
        if (session != null) {
          request.headers['Authorization'] = 'Bearer ${session.accessToken}';
        }
        handler.next(request);
      },
      onError: (error, handler) async {
        final request = error.requestOptions;
        final canRefresh =
            error.response?.statusCode == 401 &&
            request.extra['sessionRetry'] != true &&
            !request.path.startsWith('/auth/');
        if (!canRefresh) return handler.next(error);

        try {
          refreshOperation ??= refreshSession().whenComplete(
            () => refreshOperation = null,
          );
          await refreshOperation;
          final session = await storage.read();
          if (session == null) return handler.next(error);
          request.extra['sessionRetry'] = true;
          request.headers['Authorization'] = 'Bearer ${session.accessToken}';
          return handler.resolve(await dio.fetch<dynamic>(request));
        } on Object {
          await storage.clear();
          return handler.next(error);
        }
      },
    ),
  );
  ref.onDispose(() {
    dio.close(force: true);
    refreshDio.close(force: true);
  });
  return dio;
});

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/app/configuration.dart';

final dioProvider = Provider<Dio>((ref) {
  final configuration = ref.watch(appConfigurationProvider);
  final dio = Dio(
    BaseOptions(
      baseUrl: configuration.apiBaseUrl.toString(),
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
      responseType: ResponseType.json,
    ),
  );
  ref.onDispose(dio.close);
  return dio;
});

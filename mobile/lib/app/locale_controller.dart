import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/features/auth/application/auth_controller.dart';

class LocaleController extends Notifier<Locale?> {
  @override
  Locale? build() {
    final session = ref.watch(authControllerProvider).value;
    return session == null ? null : Locale(session.user.locale);
  }

  void select(String languageCode) => state = Locale(languageCode);
}

final localeProvider = NotifierProvider<LocaleController, Locale?>(
  LocaleController.new,
);

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LocaleController extends Notifier<Locale?> {
  @override
  Locale? build() => null;

  void select(String languageCode) => state = Locale(languageCode);
}

final localeProvider = NotifierProvider<LocaleController, Locale?>(
  LocaleController.new,
);

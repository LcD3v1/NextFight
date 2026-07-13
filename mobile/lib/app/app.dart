import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/app/locale_controller.dart';
import 'package:nextfight/app/router.dart';
import 'package:nextfight/app/theme/app_theme.dart';
import 'package:nextfight/l10n/app_localizations.dart';

class NextFightApp extends ConsumerWidget {
  const NextFightApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => MaterialApp.router(
    title: 'NextFight',
    debugShowCheckedModeBanner: false,
    theme: AppTheme.dark,
    locale: ref.watch(localeProvider),
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    routerConfig: ref.watch(routerProvider),
  );
}

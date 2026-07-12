import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/app/router.dart';
import 'package:nextfight/app/theme/app_theme.dart';

class NextFightApp extends ConsumerWidget {
  const NextFightApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => MaterialApp.router(
    title: 'NextFight',
    debugShowCheckedModeBanner: false,
    theme: AppTheme.dark,
    routerConfig: ref.watch(routerProvider),
  );
}

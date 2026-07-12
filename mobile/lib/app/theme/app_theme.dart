import 'package:flutter/material.dart';

abstract final class AppColors {
  static const background = Color(0xFF090A0C);
  static const surface = Color(0xFF14161A);
  static const action = Color(0xFFE53935);
  static const live = Color(0xFF35C46A);
  static const prediction = Color(0xFFFFB547);
}

abstract final class AppTheme {
  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.background,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.action,
      brightness: Brightness.dark,
      surface: AppColors.surface,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      centerTitle: false,
    ),
  );
}

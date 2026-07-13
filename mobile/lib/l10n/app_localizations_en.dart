// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'NextFight';

  @override
  String get signIn => 'Sign in';

  @override
  String get createAccount => 'Create account';

  @override
  String get email => 'Email';

  @override
  String get password => 'Password';

  @override
  String get displayName => 'Display name';

  @override
  String get events => 'Events';

  @override
  String get favorites => 'Favorites';

  @override
  String get alerts => 'Alerts';

  @override
  String get profile => 'Profile';

  @override
  String get upcomingEvents => 'Upcoming events';

  @override
  String get noEvents => 'No events available right now.';

  @override
  String get noFavorites => 'Your favorite events will appear here.';

  @override
  String get noAlerts => 'Your fight alerts will appear here.';

  @override
  String get retry => 'Try again';

  @override
  String get fightCard => 'Fight card';

  @override
  String get createAlert => 'Create alert';

  @override
  String get alertCreated => 'Alert created';

  @override
  String get favoriteAdded => 'Added to favorites';

  @override
  String get signOut => 'Sign out';

  @override
  String get language => 'Language';

  @override
  String get english => 'English';

  @override
  String get portuguese => 'Portuguese';

  @override
  String get loading => 'Loading...';

  @override
  String get live => 'LIVE';

  @override
  String get nextFight => 'Next fight';

  @override
  String get walkouts => 'Walkouts';

  @override
  String minutesBefore(int minutes) {
    return '$minutes minutes before';
  }

  @override
  String get genericError => 'Something went wrong. Please try again.';

  @override
  String get offlineError => 'You appear to be offline.';

  @override
  String get loginSubtitle => 'Choose the fight. We track the event for you.';

  @override
  String get passwordRequirements => 'Use at least 12 characters.';

  @override
  String get versus => 'vs';

  @override
  String get remove => 'Remove';

  @override
  String get forgotPassword => 'Forgot password?';

  @override
  String get resetPassword => 'Reset password';

  @override
  String get recoveryInstructions =>
      'Enter your account email. If it exists, we will send a secure recovery link.';

  @override
  String get sendRecoveryLink => 'Send recovery link';

  @override
  String get recoverySent =>
      'If the account exists, recovery instructions were sent.';

  @override
  String get recoveryToken => 'Recovery token';

  @override
  String get passwordChanged => 'Password changed. Sign in again.';
}

// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Portuguese (`pt`).
class AppLocalizationsPt extends AppLocalizations {
  AppLocalizationsPt([String locale = 'pt']) : super(locale);

  @override
  String get appName => 'NextFight';

  @override
  String get signIn => 'Entrar';

  @override
  String get createAccount => 'Criar conta';

  @override
  String get email => 'E-mail';

  @override
  String get password => 'Senha';

  @override
  String get displayName => 'Nome';

  @override
  String get events => 'Eventos';

  @override
  String get favorites => 'Favoritos';

  @override
  String get alerts => 'Alertas';

  @override
  String get profile => 'Perfil';

  @override
  String get upcomingEvents => 'Próximos eventos';

  @override
  String get noEvents => 'Nenhum evento disponível agora.';

  @override
  String get noFavorites => 'Seus eventos favoritos aparecerão aqui.';

  @override
  String get noAlerts => 'Seus alertas de lutas aparecerão aqui.';

  @override
  String get retry => 'Tentar novamente';

  @override
  String get fightCard => 'Card de lutas';

  @override
  String get createAlert => 'Criar alerta';

  @override
  String get alertCreated => 'Alerta criado';

  @override
  String get favoriteAdded => 'Adicionado aos favoritos';

  @override
  String get signOut => 'Sair';

  @override
  String get language => 'Idioma';

  @override
  String get english => 'English';

  @override
  String get portuguese => 'Português';

  @override
  String get loading => 'Carregando...';

  @override
  String get live => 'AO VIVO';

  @override
  String get nextFight => 'Próxima luta';

  @override
  String get walkouts => 'Entradas';

  @override
  String minutesBefore(int minutes) {
    return '$minutes minutos antes';
  }

  @override
  String get genericError => 'Algo deu errado. Tente novamente.';

  @override
  String get offlineError => 'Parece que você está sem conexão.';

  @override
  String get loginSubtitle =>
      'Escolha a luta. Nós acompanhamos o evento por você.';

  @override
  String get passwordRequirements => 'Use pelo menos 12 caracteres.';

  @override
  String get versus => 'vs';

  @override
  String get remove => 'Remover';
}

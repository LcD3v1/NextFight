# Mobile

Aplicativo NextFight para Android e iOS, desenvolvido em Flutter com arquitetura feature-first.

## Fundação

- Riverpod para estado e injeção de dependências;
- GoRouter para navegação declarativa;
- Dio para HTTP;
- Freezed e `json_serializable` para modelos imutáveis;
- Secure Storage para credenciais futuras;
- Firebase Messaging para push após configuração oficial por ambiente;
- tema escuro e estados reutilizáveis de loading, vazio, erro, offline, sucesso e dado desatualizado.

## Ambientes

Valores são fornecidos em compile time:

```powershell
flutter run --dart-define=APP_ENV=local --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

Ambientes aceitos: `local`, `development`, `staging` e `production`. No emulador Android, `10.0.2.2` representa a máquina host.

## Qualidade

```powershell
flutter pub get
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
flutter build apk --debug
```

Não há telas finais nem dados falsos nesta fundação. Credenciais Firebase devem ser geradas para cada ambiente antes de inicializar push notifications.

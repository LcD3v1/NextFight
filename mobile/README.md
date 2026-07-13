# Mobile

Aplicativo NextFight para Android e iOS, desenvolvido em Flutter com arquitetura feature-first.

## Recursos da Fase 1

- cadastro, login, logout e renovação automática da sessão JWT;
- credenciais armazenadas no Secure Storage do sistema;
- eventos, detalhes e card de lutas consumidos da API real;
- favoritos e alertas do usuário;
- atualização por WebSocket somente durante eventos ao vivo;
- registro de dispositivos no FCM/APNs quando a configuração Firebase está disponível;
- interface em português e inglês;
- estados de carregamento, vazio e erro, com atualização por gesto.

O código é organizado por funcionalidade e separa apresentação, aplicação, dados e domínio. Riverpod gerencia estado e dependências, GoRouter controla a navegação e Dio concentra HTTP, autenticação e renovação de token.

## Ambientes

As configurações são fornecidas em tempo de compilação. Valores aceitos para `APP_ENV`: `local`, `development`, `staging` e `production`.

No emulador Android, `10.0.2.2` representa a máquina host:

```powershell
flutter run --dart-define=APP_ENV=local --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

Para Windows ou navegador local, use `http://localhost:8000/api/v1`.

## Push notifications

Os arquivos fornecidos pelos projetos Firebase não são versionados:

- Android: `android/app/google-services.json`;
- iOS: `ios/Runner/GoogleService-Info.plist`.

Use um projeto Firebase separado por ambiente. Sem esses arquivos, o aplicativo continua funcionando localmente e apenas ignora o registro de push.

## Qualidade

```powershell
flutter pub get
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
flutter build apk --debug --dart-define=APP_ENV=local --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

No Windows, a compilação Android exige `JAVA_HOME` apontando para um JDK. O Android Studio inclui um em `C:\Program Files\Android\Android Studio\jbr`.

# Aplicativo Mobile

## Stack

- Flutter.
- Riverpod para estado e injeção.
- GoRouter para navegação.
- Dio para HTTP.
- Freezed e json_serializable para modelos.
- Firebase Messaging para push.
- Secure Storage para tokens.

## Estrutura feature-first

```text
lib/
  app/
  core/
  features/
    auth/
    events/
    fights/
    alerts/
    favorites/
    profile/
    subscriptions/
```

## Telas do MVP

- Splash.
- Onboarding.
- Login e cadastro.
- Home.
- Eventos.
- Detalhe do evento.
- Detalhe da luta.
- Criar alerta.
- Favoritos.
- Histórico de alertas.
- Perfil e configurações.
- Paywall futuro.

## Estados obrigatórios

Toda tela remota deve tratar:

- loading;
- vazio;
- erro;
- offline;
- sucesso;
- dados desatualizados.

## Realtime

O app mantém WebSocket apenas quando necessário. Em segundo plano, depende de push e atualização ao retornar.

# Mobile

Aplicativo NextFight para iOS e Android, desenvolvido em Flutter.

## Responsabilidade

Este módulo será responsável pela experiência do usuário, navegação, consumo da API, atualizações em tempo real, armazenamento seguro de credenciais e notificações push.

## Arquitetura prevista

A organização será feature-first, com áreas compartilhadas em `app` e `core`. Cada feature terá limites explícitos entre apresentação, aplicação, domínio e acesso a dados, sem abstrações que não tragam benefício concreto.

As decisões obrigatórias estão em `docs/09-MOBILE.md`: Riverpod, GoRouter, Dio, Freezed, `json_serializable`, Firebase Messaging e Secure Storage.

## Estado atual

A aplicação Flutter ainda não foi inicializada. Isso pertence à etapa “Fundação do mobile” de `docs/19-INITIAL-CODEX-PROMPTS.md`; esta etapa cria apenas os limites do monorepo.

Quando inicializado, o módulo deverá ser validado com:

```powershell
flutter pub get
flutter analyze
flutter test
```

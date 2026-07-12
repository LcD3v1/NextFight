# Arquitetura

## Decisão principal

O MVP será um monólito modular com limites de domínio claros.

## Componentes

```text
Flutter App
    |
API Gateway / FastAPI
    |
+-- Identity Module
+-- Users Module
+-- Organizations Module
+-- Events Module
+-- Fights Module
+-- Alerts Module
+-- Monitoring Module
+-- Predictions Module
+-- Notifications Module
+-- Subscriptions Module
+-- Admin Module
+-- Analytics Module
    |
PostgreSQL + Redis + Object Storage
```

## Backend

Cada módulo deve conter:

- domínio;
- casos de uso;
- interfaces;
- infraestrutura;
- rotas;
- schemas;
- testes.

## Fluxo de atualização ao vivo

1. Provedor ou operador envia mudança.
2. Monitoring Module valida a transição.
3. Estado atual é persistido.
4. Um evento de domínio é publicado.
5. Prediction Module recalcula previsões.
6. Alerts Module identifica usuários afetados.
7. Notification Module envia notificações.
8. WebSocket publica atualização aos clientes conectados.

## Redis

Usos permitidos:

- cache;
- locks distribuídos;
- filas;
- rate limiting;
- sessões efêmeras de WebSocket.

Redis não será a fonte principal de verdade.

## Idempotência

Toda alteração ao vivo e todo disparo de alerta deve possuir chave idempotente.

## Escalabilidade futura

Primeiros candidatos a separação:

1. Monitoring Service.
2. Notification Service.
3. Prediction Service.
4. Provider Ingestion Service.

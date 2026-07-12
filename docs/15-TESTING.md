# Testes

## Backend

- Unitários para domínio e previsão.
- Integração para banco e Redis.
- Contrato para provedores externos.
- End-to-end para fluxos críticos.

## Mobile

- Unitários para regras locais.
- Widget tests.
- Integration tests para login, eventos e alertas.

## Admin

- Unitários com Vitest.
- Componentes críticos.
- Playwright para operação ao vivo.

## Cenários críticos

- Nocaute rápido altera previsão.
- Luta cancelada muda próxima luta.
- Card reordenado.
- Evento pausado.
- Provedor envia evento duplicado.
- Retry de notificação não duplica alerta.
- Operador corrige estado automático.

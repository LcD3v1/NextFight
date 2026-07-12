# Notificações e Alertas

## Tipos de gatilho

- fixed_minutes_before_estimate
- previous_fight_started
- previous_fight_completed
- fight_is_next
- walkouts_started
- fight_started
- card_changed
- fight_cancelled

## Canais

- Push notification.
- Notificação local quando possível.
- E-mail apenas para comunicações não urgentes.
- Ligação telefônica como recurso futuro premium.

## Regras

- O mesmo gatilho não pode ser enviado duas vezes.
- Toda entrega deve ter idempotency key.
- Preferências de silêncio e idioma devem ser respeitadas.
- O usuário deve poder testar notificações.
- Tokens inválidos devem ser desativados.

## Mensagem de exemplo

Título: Sua luta é a próxima  
Corpo: A luta anterior terminou. Nova previsão: 12 a 18 minutos.

## Falhas

- Retry com backoff.
- Dead-letter queue.
- Métricas por plataforma e código de erro.

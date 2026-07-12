# Motor de Monitoramento

## Objetivo

Manter o estado confiável de cada evento e luta.

## Fontes

- Provedor externo.
- Operador humano.
- Fonte secundária futura.

## Prioridade de fonte

A prioridade será configurável. Correções manuais devem prevalecer por uma janela definida para evitar que o provedor sobrescreva imediatamente a correção.

## Máquina de estados do evento

- scheduled
- delayed
- live
- paused
- completed
- cancelled

## Máquina de estados da luta

- scheduled
- next
- walkouts
- live
- paused
- completed
- cancelled
- no_contest

## Regras críticas

- Transições inválidas devem ser rejeitadas ou exigir override administrativo.
- Cada entrada recebe source, timestamp e idempotency key.
- Reordenação do card gera histórico.
- O motor deve recalcular a próxima luta após cada transição.

## Polling

- Eventos inativos: baixa frequência.
- Próximos do início: frequência moderada.
- Eventos ao vivo: alta frequência conforme limites do provedor.

## Fallback

Se a fonte automática ficar indisponível:

1. marcar o evento como dados possivelmente atrasados;
2. alertar operadores;
3. manter último estado conhecido;
4. permitir operação manual.

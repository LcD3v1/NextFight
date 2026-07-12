# Segurança

## Controles mínimos

- HTTPS obrigatório.
- Segredos em variáveis seguras.
- Argon2id.
- JWT curto e refresh rotativo.
- Rate limiting.
- CORS restritivo.
- Validação de payload.
- Proteção contra enumeração de contas.
- Auditoria administrativa.
- Dependências verificadas automaticamente.

## Dados pessoais

Coletar apenas o necessário. Permitir exportação e exclusão de conta.

## Administração

- MFA obrigatório para administradores quando implementado.
- Sessões administrativas curtas.
- Registro de IP, usuário, ação, entidade e diff.

## Incidentes

Manter procedimento para:

- revogar tokens;
- desativar provedor;
- bloquear envios;
- restaurar backup;
- comunicar falhas relevantes.

# Infraestrutura

## Desenvolvimento local

Docker Compose com:

- backend;
- PostgreSQL;
- Redis;
- worker;
- admin;
- Mailpit opcional.

## Ambientes

- local;
- development;
- staging;
- production.

## Produção inicial

Pode usar serviços gerenciados para reduzir operação:

- container hosting;
- PostgreSQL gerenciado;
- Redis gerenciado;
- object storage compatível com S3;
- CDN;
- serviço de logs e erros.

## Observabilidade

- logs JSON;
- métricas;
- health checks;
- tracing futuro;
- alertas de falha de provedor e fila.

## Backup

- backup diário;
- retenção definida;
- teste periódico de restauração.

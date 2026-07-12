# Prompts iniciais para o Codex

## Prompt 01 — Criar o monorepo

Leia `README.md` e todos os arquivos em `docs/`. Crie a estrutura inicial do monorepo NextFight com as pastas `mobile`, `backend`, `admin`, `infrastructure` e `packages`. Configure arquivos `.gitignore`, `.editorconfig`, documentação de execução local e Docker Compose inicial. Não implemente funcionalidades de negócio ainda. Garanta que a estrutura criada esteja alinhada com `docs/05-ARCHITECTURE.md` e `docs/17-CODING-STANDARDS.md`.

## Prompt 02 — Fundação do backend

Leia toda a documentação relevante. Inicialize o backend em FastAPI com Python 3.12+, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL, Redis, Ruff, Pyright e pytest. Crie configuração por ambiente, logs estruturados, health checks, request ID, tratamento global de erros e estrutura modular. Não implemente autenticação ainda. Execute testes e linters.

## Prompt 03 — Fundação do mobile

Leia `docs/09-MOBILE.md`, `docs/03-BRANDING.md` e `docs/17-CODING-STANDARDS.md`. Inicialize o app Flutter com Riverpod, GoRouter, Dio, Freezed, json_serializable e Secure Storage. Crie tema escuro inicial, tokens de design, navegação base e estados reutilizáveis de loading, erro, vazio e offline. Não implemente telas finais ainda.

## Prompt 04 — Fundação do admin

Leia `docs/10-ADMIN.md`. Inicialize React + TypeScript + Vite + Tailwind + shadcn/ui + TanStack Query + React Hook Form + Zod. Crie layout autenticado, sidebar, topbar, tema escuro e páginas placeholder para as áreas administrativas. Não use dados falsos permanentes; mantenha adaptadores claros para integração futura.

## Prompt 05 — Banco inicial

Leia `docs/06-DATABASE.md`. Implemente as entidades iniciais, migrations e repositories para users, devices, organizations, athletes, events, fights, alerts e audit logs. Use UUID, timestamptz, constraints, índices e enums de estado. Crie testes de integração.

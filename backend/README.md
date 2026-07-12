# Backend

API e processamento assíncrono do NextFight, implementados como um monólito modular em Python e FastAPI.

## Responsabilidade

Este módulo concentra regras de domínio, casos de uso, persistência, integrações, API HTTP, WebSockets e workers. PostgreSQL é a fonte de verdade; Redis é usado somente para cache, filas, locks, rate limiting e estado efêmero.

## Arquitetura

O código utiliza layout `src` e separação por responsabilidade:

```text
src/nextfight/
  api/                 # Composição das rotas HTTP
  core/                # Configuração, erros, logs e middleware
  infrastructure/      # PostgreSQL, Redis e integrações técnicas
  modules/             # Módulos do monólito organizados por domínio
```

Cada módulo de negócio deve isolar domínio, aplicação, interfaces e infraestrutura quando essas camadas forem necessárias. Dependências entre módulos ocorrem por contratos explícitos e eventos de domínio. Não é permitido acessar tabelas ou implementações internas de outro módulo diretamente.

## Requisitos

- Python 3.12;
- uv 0.11+;
- PostgreSQL 17;
- Redis 7.4.

## Instalação

Na raiz do monorepo, inicie PostgreSQL e Redis:

```powershell
docker compose up -d postgres redis
```

No diretório `backend`:

```powershell
uv python install 3.12
uv sync --locked --all-groups
```

## Execução

```powershell
uv run uvicorn nextfight.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints operacionais:

- `GET /health/live`: confirma que o processo está ativo;
- `GET /health/ready`: confirma acesso ao PostgreSQL e Redis;
- `GET /docs`: documentação OpenAPI, disponível fora de produção.

Também é possível executar o backend com toda a infraestrutura:

```powershell
docker compose up -d --build
```

## Qualidade

```powershell
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

Os testes de integração usam PostgreSQL e Redis reais configurados por `DATABASE_URL` e `REDIS_URL`. Não utilizam banco em memória nem substitutos das dependências externas.

## Migrações

Quando existirem modelos persistentes:

```powershell
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "describe change"
```

Migrações devem ser revisadas antes de execução e nunca devem depender da importação de dados falsos.

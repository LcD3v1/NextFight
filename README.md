# NextFight

NextFight é uma plataforma para acompanhar esportes de combate em tempo real e receber alertas inteligentes conforme o andamento dos eventos.

## Monorepo

| Diretório | Responsabilidade |
| --- | --- |
| `mobile/` | Aplicativo Flutter para iOS e Android. |
| `backend/` | Monólito modular FastAPI e workers assíncronos. |
| `admin/` | Painel operacional React e TypeScript. |
| `infrastructure/` | Recursos de deploy e observabilidade. |
| `packages/` | Contratos e recursos compartilhados. |
| `docs/` | Produto, arquitetura e engenharia. |

PostgreSQL é a fonte de verdade. Redis mantém apenas estado efêmero, rate limiting e coordenação. O backend é um monólito modular com limites de domínio claros.

## Início rápido

Requisitos: Git, Docker Engine 24+ e Docker Compose v2. Flutter stable e o JDK do Android Studio são necessários apenas para executar o mobile fora de contêiner.

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
Invoke-RestMethod http://localhost:8000/health/ready
```

O Compose inicia PostgreSQL, Redis, aplica as migrações, inicia o backend e publica o painel:

- API: `http://localhost:8000`;
- OpenAPI local: `http://localhost:8000/docs`;
- painel: `http://localhost:5173`.

Para encerrar sem apagar dados:

```powershell
docker compose down
```

Consulte [docs/20-LOCAL-DEVELOPMENT.md](docs/20-LOCAL-DEVELOPMENT.md) para o fluxo completo.

## Ambientes e segurança

O projeto reconhece `local`, `development`, `staging` e `production`. Arquivos `.env` reais nunca são versionados. Development, staging e production devem receber segredos por um gerenciador seguro. As credenciais do `.env.example` servem somente para execução local.

## Convenções

- Código, identificadores e mensagens técnicas em inglês.
- Documentação e comunicação do produto em português.
- Commits no padrão Conventional Commits.
- Alterações arquiteturais devem atualizar `docs/18-DECISIONS.md`.
- Dependências devem respeitar `docs/05-ARCHITECTURE.md`.

Leia primeiro `docs/00-CODEX-INSTRUCTIONS.md` e `docs/21-REPOSITORY-CONVENTIONS.md`.

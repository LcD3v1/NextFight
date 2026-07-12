# NextFight

NextFight é uma plataforma para acompanhar esportes de combate em tempo real e receber alertas inteligentes baseados no andamento real dos eventos.

## Estrutura do monorepo

| Diretório | Responsabilidade |
| --- | --- |
| `mobile/` | Aplicativo Flutter para iOS e Android. |
| `backend/` | Monólito modular em FastAPI e seus workers. |
| `admin/` | Painel administrativo em React e TypeScript. |
| `infrastructure/` | Recursos de execução, deploy e observabilidade. |
| `packages/` | Contratos e recursos compartilhados entre clientes. |
| `docs/` | Documentação de produto, arquitetura e engenharia. |

O PostgreSQL é a fonte de verdade. Redis é usado somente para dados efêmeros, como cache, filas e locks. O backend começa como um monólito modular com limites de domínio claros.

## Pré-requisitos

- Git;
- Docker Engine 24+ com Docker Compose v2;
- Flutter stable, para o aplicativo mobile;
- Python 3.12+, para o backend;
- Node.js LTS, para o painel administrativo.

Flutter, Python e Node.js só serão necessários quando as respectivas fundações forem inicializadas. Nesta etapa, a execução local disponibiliza PostgreSQL e Redis.

## Início rápido

1. Crie a configuração local:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Revise os valores locais de `.env`. Os valores de exemplo não devem ser usados fora do ambiente local.

3. Inicie a infraestrutura:

   ```powershell
   docker compose up -d
   ```

4. Verifique os serviços:

   ```powershell
   docker compose ps
   docker compose exec postgres pg_isready -U nextfight -d nextfight
   docker compose exec redis redis-cli ping
   ```

5. Encerre os contêineres sem apagar os dados:

   ```powershell
   docker compose down
   ```

Consulte [docs/20-LOCAL-DEVELOPMENT.md](docs/20-LOCAL-DEVELOPMENT.md) para execução detalhada e solução de problemas.

## Ambientes

O projeto reconhece `local`, `development`, `staging` e `production`. Configurações públicas podem ser versionadas; segredos devem ser fornecidos pelo ambiente de execução ou por um gerenciador de segredos. Nenhum arquivo `.env` real deve ser versionado.

## Convenções

- Código, identificadores e mensagens técnicas em inglês.
- Documentação e comunicação do produto em português.
- Commits no padrão Conventional Commits.
- Alterações arquiteturais devem ser registradas primeiro em `docs/18-DECISIONS.md`.
- Dependências entre módulos devem respeitar os limites descritos em `docs/05-ARCHITECTURE.md`.

Leia [docs/21-REPOSITORY-CONVENTIONS.md](docs/21-REPOSITORY-CONVENTIONS.md) antes de contribuir.

## Ordem de leitura

1. `docs/00-CODEX-INSTRUCTIONS.md`
2. `docs/01-PRD.md`
3. `docs/02-VISION.md`
4. `docs/05-ARCHITECTURE.md`
5. `docs/06-DATABASE.md`
6. `docs/07-API.md`
7. Demais documentos relevantes para a tarefa.

Nenhuma implementação deve contradizer a documentação. Quando uma decisão mudar, atualize primeiro `docs/18-DECISIONS.md` e depois os documentos afetados.

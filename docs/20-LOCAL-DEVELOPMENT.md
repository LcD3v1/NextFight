# Desenvolvimento local

## Requisitos

- Docker Engine 24+ e Docker Compose v2;
- portas `5432`, `6379`, `8000` e `5173` disponíveis;
- Flutter stable e JDK do Android Studio para o aplicativo mobile.

## Serviços locais

Na raiz do repositório:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

O backend aplica as migrações Alembic antes de iniciar. Endereços padrão:

- API: `http://localhost:8000`;
- painel: `http://localhost:5173`;
- PostgreSQL: `localhost:5432`;
- Redis: `localhost:6379`.

## Verificação

```powershell
docker compose exec postgres pg_isready -U nextfight -d nextfight
docker compose exec redis redis-cli ping
Invoke-RestMethod http://localhost:8000/health/ready
```

## Mobile

No diretório `mobile`:

```powershell
flutter pub get
flutter run --dart-define=APP_ENV=local --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

`10.0.2.2` representa a máquina host no emulador Android. Para Windows ou navegador, use `http://localhost:8000/api/v1`. Os arquivos Firebase são específicos por ambiente e não são versionados; consulte `mobile/README.md`.

## Qualidade

Backend, no diretório `backend`:

```powershell
uv sync --locked --all-groups
uv run ruff format --check src tests
uv run ruff check src tests
uv run pyright
uv run pytest
```

Admin, no diretório `admin`:

```powershell
npm ci
npm run lint
npm run typecheck
npm run test -- --run
npm run build
```

Mobile, no diretório `mobile`:

```powershell
flutter analyze
flutter test
flutter build apk --debug --dart-define=APP_ENV=local --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

## Operação

```powershell
docker compose logs -f backend admin postgres redis
docker compose down
```

Use `docker compose down -v` somente quando quiser apagar permanentemente os dados locais.

O projeto reconhece `local`, `development`, `staging` e `production`. Ambientes compartilhados devem receber segredos pelo mecanismo seguro da plataforma, nunca por arquivos versionados.

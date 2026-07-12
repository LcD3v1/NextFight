# Desenvolvimento local

## Objetivo

Este guia descreve a execução local do monorepo. Nesta fase, somente PostgreSQL e Redis possuem serviços executáveis; aplicações serão adicionadas nas etapas de fundação correspondentes.

## Requisitos

- Docker Engine 24 ou superior;
- Docker Compose v2;
- portas `5432` e `6379` disponíveis, ou portas alternativas configuradas no `.env`.

## Configuração

Na raiz do repositório, copie o modelo de ambiente:

```powershell
Copy-Item .env.example .env
```

Em Bash:

```bash
cp .env.example .env
```

O arquivo `.env` é local e ignorado pelo Git. As credenciais fornecidas no exemplo servem exclusivamente para desenvolvimento local.

## Iniciar

```powershell
docker compose up -d
docker compose ps
```

O PostgreSQL ficará disponível em `localhost:5432` e o Redis em `localhost:6379`, salvo alteração no `.env`.

## Verificar saúde

```powershell
docker compose exec postgres pg_isready -U nextfight -d nextfight
docker compose exec redis redis-cli ping
```

O primeiro comando deve informar que o PostgreSQL aceita conexões. O segundo deve retornar `PONG`.

## Logs

```powershell
docker compose logs -f postgres redis
```

## Encerrar

Para manter os dados locais:

```powershell
docker compose down
```

Para apagar também os volumes, após confirmar que os dados locais são descartáveis:

```powershell
docker compose down -v
```

## Ambientes

O valor `NEXTFIGHT_ENV` identifica o ambiente:

- `local`: execução na máquina do desenvolvedor;
- `development`: ambiente compartilhado de integração;
- `staging`: validação anterior à produção;
- `production`: produção.

Arquivos `.env` não devem ser usados para distribuir segredos de ambientes compartilhados. Development, staging e production devem receber segredos por mecanismos seguros da plataforma de hospedagem. Configurações específicas serão adicionadas juntamente com a infraestrutura desses ambientes.

## Solução de problemas

Se uma porta estiver ocupada, altere `POSTGRES_PORT` ou `REDIS_PORT` no `.env` e reinicie o Compose. Se um serviço não ficar saudável, consulte seus logs e confirme que os volumes possuem permissão de escrita.

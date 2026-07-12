# Infrastructure

Recursos de execução local, entrega, observabilidade e operação do NextFight.

## Responsabilidade

Este módulo abrigará configurações de contêineres, CI/CD, ambientes, observabilidade, backups e, quando adotado, infraestrutura como código. Segredos nunca devem ser armazenados neste diretório.

Os diretórios em `environments/` reservam limites explícitos para `local`, `development`, `staging` e `production`. Recursos concretos serão incluídos quando a plataforma de hospedagem for decidida e registrada em ADR.

## Estado atual

O arquivo `compose.yaml` na raiz disponibiliza PostgreSQL e Redis com persistência, rede isolada e health checks. Serviços de aplicação serão adicionados quando backend e admin tiverem fundações executáveis, evitando imagens e comandos fictícios.

## Operação local

```powershell
docker compose up -d
docker compose ps
docker compose logs -f postgres redis
docker compose down
```

`docker compose down -v` apaga permanentemente os volumes locais e só deve ser usado quando a perda dos dados de desenvolvimento for intencional.

# Backend

API e processamento assíncrono do NextFight, implementados como um monólito modular em Python e FastAPI.

## Responsabilidade

Este módulo concentrará regras de domínio, casos de uso, persistência, integrações, API HTTP, WebSockets e workers. PostgreSQL será a fonte de verdade; Redis será usado para cache, filas, locks, rate limiting e estado efêmero.

## Arquitetura prevista

Os módulos de negócio terão domínio, aplicação, interfaces e infraestrutura claramente separados. Dependências entre módulos ocorrerão por contratos explícitos e eventos de domínio. O desenho deve permitir extrações futuras sem introduzir microsserviços no MVP.

Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, Ruff, Pyright e pytest são obrigatórios conforme `docs/17-CODING-STANDARDS.md`.

## Estado atual

A aplicação FastAPI ainda não foi inicializada. Isso pertence à etapa “Fundação do backend” de `docs/19-INITIAL-CODEX-PROMPTS.md`; esta etapa disponibiliza PostgreSQL e Redis para desenvolvimento local.

Após a fundação, este documento deverá registrar os comandos efetivos de instalação, migração, API, worker, lint, tipagem e testes.

# Instruções permanentes para o Codex

Você está trabalhando no projeto **NextFight**, uma plataforma profissional para acompanhar esportes de combate em tempo real.

## Objetivo

Construir um produto confiável, escalável e seguro que permita ao usuário escolher uma luta e receber alertas com base no andamento real do evento.

## Regras obrigatórias

1. Leia os documentos relevantes antes de alterar código.
2. Nunca implemente funcionalidades fora do escopo solicitado.
3. Não use código temporário, pseudocódigo ou TODO sem justificativa explícita.
4. Não introduza dependências sem explicar o motivo.
5. Preserve compatibilidade com a arquitetura definida.
6. Garanta tipagem, validação, tratamento de erros, logs e testes.
7. Não exponha segredos, tokens ou credenciais.
8. Não use mocks em produção.
9. Toda alteração de contrato deve atualizar API, modelos, testes e documentação.
10. Ao concluir uma tarefa, informe:
   - arquivos criados;
   - arquivos alterados;
   - decisões tomadas;
   - testes executados;
   - limitações restantes.

## Padrões técnicos

- Mobile: Flutter + Dart.
- Backend: Python + FastAPI.
- Banco: PostgreSQL.
- Cache e filas: Redis.
- Realtime: WebSockets.
- Admin: React + TypeScript + Tailwind + shadcn/ui.
- Infraestrutura inicial: Docker Compose.
- Testes: pytest, Flutter test e Vitest/Playwright.

## Arquitetura

O MVP será um **monólito modular**, preparado para futura separação em serviços. Não criar microserviços prematuramente.

## Segurança

- JWT de curta duração e refresh token rotativo.
- Senhas com Argon2id.
- Rate limiting.
- Auditoria de ações administrativas.
- Validação estrita de entrada.
- Princípio do menor privilégio.

## Qualidade

- SOLID quando aplicável.
- Clean Architecture sem excesso de abstração.
- Feature-first.
- Funções e classes pequenas.
- Nomes explícitos.
- Cobertura de testes para regras críticas.

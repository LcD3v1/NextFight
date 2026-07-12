# Convenções do repositório

## Idioma

- Código, nomes de arquivos técnicos, identificadores, logs e mensagens de erro: inglês.
- Documentação de produto e engenharia: português.
- Textos exibidos ao usuário: sempre preparados para internacionalização.

## Organização

- Organizar aplicações por feature e domínio.
- Evitar dependências circulares e acesso direto à infraestrutura de outro módulo.
- Compartilhar somente contratos estáveis e recursos realmente reutilizados.
- Manter arquivos pequenos, coesos e com responsabilidade única.
- Registrar decisões arquiteturais em `docs/18-DECISIONS.md` antes de alterar a arquitetura documentada.

## Configuração e ambientes

- Ambientes aceitos: `local`, `development`, `staging` e `production`.
- Configurações devem vir do ambiente e ser validadas na inicialização.
- Segredos, credenciais reais e arquivos `.env` nunca são versionados.
- PostgreSQL é a fonte da verdade; Redis armazena apenas estado efêmero.

## Qualidade

Cada alteração deve executar as validações aplicáveis ao módulo:

- backend: Ruff, Pyright e pytest;
- mobile: formatter, analyzer e Flutter test;
- admin: formatter, ESLint, verificação de tipos, Vitest e, nos fluxos críticos, Playwright;
- infraestrutura: validação sintática e inspeção da configuração renderizada.

Não é permitido silenciar verificações sem justificativa documentada. Regras críticas exigem testes automatizados.

## Git

Branches de longa duração:

- `main`: versão pronta para produção;
- `develop`: integração, enquanto este fluxo for necessário.

Branches de trabalho usam `feature/<description>` ou `fix/<description>`. Commits seguem Conventional Commits, por exemplo:

```text
feat(events): add event timeline endpoint
fix(alerts): prevent duplicate notification delivery
docs(repository): clarify local setup
```

Commits devem ser pequenos, revisáveis e não misturar uma feature com refatorações amplas não relacionadas.

## Pull requests

Uma alteração está pronta para revisão quando:

1. respeita os documentos de arquitetura e segurança;
2. não contém segredos, dados falsos permanentes ou código morto;
3. possui documentação e testes proporcionais ao risco;
4. passa por lint, tipagem, testes e build aplicáveis;
5. descreve migrações, riscos operacionais e estratégia de reversão quando relevantes.

## Dependências

Toda nova dependência precisa ter finalidade clara, manutenção ativa, licença compatível e impacto de segurança avaliado. Prefira recursos da linguagem e dependências já adotadas quando atenderem ao requisito sem comprometer clareza.

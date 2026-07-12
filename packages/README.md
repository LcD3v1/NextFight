# Packages

Contratos e recursos compartilhados do monorepo NextFight.

## Responsabilidade

Este diretório poderá conter especificações de API, schemas independentes de linguagem, configurações comuns e SDKs gerados. Não deve se tornar um depósito de utilitários genéricos nem acoplar Flutter, backend e admin por detalhes internos.

## Regras

- A API publicada é a fonte dos contratos entre clientes e backend.
- Alterações de contrato devem atualizar modelos, validações, testes e documentação.
- Código gerado deve identificar sua origem e possuir um processo reproduzível de geração.
- Regras de negócio permanecem no backend; clientes não compartilham implementação de domínio.

## Estado atual

Não há pacotes compartilhados porque nenhum contrato executável foi criado nesta etapa. Novos pacotes devem possuir finalidade, proprietário, versionamento e validações documentados em seu próprio `README.md`.

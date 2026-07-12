# Environments

Configurações de infraestrutura são separadas por ambiente para impedir que parâmetros locais sejam promovidos acidentalmente.

- `local`: infraestrutura executada pelo Docker Compose da raiz.
- `development`: integração compartilhada e validação contínua.
- `staging`: ambiente semelhante à produção para homologação.
- `production`: cargas reais, com controles reforçados de acesso, disponibilidade e recuperação.

Segredos não pertencem a estes diretórios. Cada ambiente deve recebê-los por um gerenciador de segredos e validar todas as variáveis obrigatórias antes de iniciar serviços.

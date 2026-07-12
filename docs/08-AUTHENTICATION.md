# Autenticação e Autorização

## Autenticação

- E-mail e senha no MVP.
- Access token JWT curto.
- Refresh token rotativo e revogável.
- Argon2id para senha.
- Verificação de e-mail.
- Recuperação de senha com token de uso único.

## Perfis

- user
- operator
- admin
- super_admin

## Regras

- Operadores só alteram eventos atribuídos quando essa regra estiver ativa.
- Toda ação administrativa sensível gera audit log.
- Tokens de dispositivo devem ser vinculados ao usuário e plataforma.
- Sessões suspeitas podem ser revogadas.

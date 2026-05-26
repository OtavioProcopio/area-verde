# Security Policy

## Regras

- Nunca commitar `.env` real.
- Nunca commitar senha.
- Nunca commitar token.
- Nunca commitar certificado.
- Nunca commitar chave privada.
- Nunca commitar secrets de deploy.
- Usar `.env.example` sem valores sensíveis.
- Secrets reais devem ficar fora do repositório.

## Revisão antes de PR

- Verifique `git diff`.
- Verifique `git status`.
- Confirme que arquivos locais sensíveis não foram adicionados.
- Prefira variáveis de ambiente para credenciais.

## Exemplos de arquivos proibidos

- `.env`
- `*.pem`
- `*.key`
- arquivos com tokens pessoais
- dumps de banco com dados reais

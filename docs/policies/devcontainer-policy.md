# DevContainer Policy

## Regras

- Use o VS Code DevContainer quando possível.
- Não dependa de configuração oculta da máquina local.
- Não commitar `.env` real.
- Use `.env.example` como referência.
- Valide Docker Compose antes de finalizar mudanças relevantes.

## Comandos úteis

```bash
cd app
docker compose config
make docker-build
make up
make down
```

## Boas práticas

- Mantenha dependências declaradas em arquivos do projeto.
- Não instale ferramentas necessárias apenas localmente.
- Documente qualquer requisito novo de ambiente.

# Banco de Dados e Migrations

## Banco principal

O projeto usa PostgreSQL como banco principal e SQLModel como camada ORM.

## Alembic

Migrations ficam em:

```text
app/migrations/versions/
```

## Criar migration

Execute dentro de `app/`:

```bash
alembic revision -m "descricao_da_migration"
```

Depois edite o arquivo gerado com operações explícitas de `upgrade` e
`downgrade`.

## Aplicar migration

Em ambiente Docker:

```bash
cd app
make migrate
```

Ou diretamente:

```bash
alembic upgrade head
```

## Regras

- Não alterar schema manualmente no banco.
- Toda alteração estrutural deve ter migration reversível.
- Revisar FKs, índices e constraints antes de abrir PR.
- Não criar tabela fora do escopo do módulo.
- Não apagar dados históricos sem decisão explícita.

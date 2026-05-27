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

## Migrations atuais do MVP

| Revision | Módulo | Resumo |
|---|---|---|
| `a1b2c3d4e5f6` | Schema inicial | Tabelas base de configuração, categorias, produtos, estoque, comandas, caixa e pagamentos |
| `b2c3d4e5f6a7` | Produtos e Categorias | Índices e regras do cadastro de produtos |
| `c3d4e5f6a7b8` | Estoque | Índices de movimentos de estoque |
| `d4e5f6a7b8c9` | Comandas | Cancelamento, atualização de itens e índices de comanda |
| `f58650a646fe` | Pagamentos | `caixa_id` opcional, observação e índices de pagamentos |

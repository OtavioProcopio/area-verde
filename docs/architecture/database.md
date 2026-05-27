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
- Seguir a [Migration Policy](../policies/migration-policy.md) antes de criar ou editar migrations.

## Migrations atuais do MVP

| Revision | Módulo | Resumo |
|---|---|---|
| `a1b2c3d4e5f6` | Schema inicial | Tabelas base de configuração, categorias, produtos, estoque, comandas, caixa e pagamentos |
| `b2c3d4e5f6a7` | Produtos e Categorias | Índices e regras do cadastro de produtos |
| `c3d4e5f6a7b8` | Estoque | Índices de movimentos de estoque |
| `d4e5f6a7b8c9` | Comandas | Cancelamento, atualização de itens e índices de comanda |
| `f58650a646fe` | Pagamentos | `caixa_id` opcional, observação e índices de pagamentos |
| `e6f7a8b9c0d1` | Caixa Diário | Índices de caixa, movimentos de caixa e vínculo de pagamento |
| `g7h8i9j0k1l2` | Clientes e Fiado | Tabela `cliente`, vínculo opcional em `comanda` e índices |
| `h8i9j0k1l2m3` | Rastreabilidade de Comanda | `caixa_origem_id`, `pendente_em`, FK e índices para relatórios futuros |

## Campos relevantes do fluxo atual

- `cliente`: cadastro simples de clientes ativos/inativos.
- `comanda.cliente_id`: vínculo opcional com cliente cadastrado.
- `comanda.nome_cliente_snapshot`: nome operacional do cliente cadastrado no momento do vínculo.
- `comanda.caixa_origem_id`: caixa aberto no momento da criação da comanda.
- `comanda.pendente_em`: data e hora em que a comanda virou fiado.

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
| `i9j0k1l2m3n4` | Produtos Compostos | `tipo_produto` em `produto` e tabela `produto_composicao` |

## Campos relevantes do fluxo atual

- `cliente`: cadastro simples de clientes ativos/inativos.
- `comanda.cliente_id`: vínculo opcional com cliente cadastrado.
- `comanda.nome_cliente_snapshot`: nome operacional do cliente cadastrado no momento do vínculo.
- `comanda.caixa_origem_id`: caixa aberto no momento da criação da comanda.
- `comanda.pendente_em`: data e hora em que a comanda virou fiado.
- `comanda.vencimento_em`: vencimento da pendência de fiado.
- `caixa.comandas_origem`: relacionamento operacional das comandas abertas
  durante o caixa.
- `produto.tipo_produto`: diferencia `SIMPLES` e `COMPOSTO`.
- `produto_composicao.quantidade_baixa`: quantidade de cada componente baixada
  por unidade vendida do produto composto.
- `movimento_estoque.produto_id`: aponta para o produto fisicamente
  movimentado. Em venda de composto, aponta para o componente, nao para o
  produto pai.

## Entidades reais

| Entidade | Tabela | Modulo principal | Observacao |
|---|---|---|---|
| `ConfiguracaoSistema` | `configuracao_sistema` | Configuracoes / Acesso | Parametros operacionais e hash da senha unica do MVP |
| `CategoriaProduto` | `categoria_produto` | Produtos e Categorias | Possui produtos |
| `Produto` | `produto` | Produtos / Estoque | Base de venda, controle de estoque e tipo simples/composto |
| `ProdutoComposicao` | `produto_composicao` | Produtos Compostos | Componentes e quantidade de baixa por produto composto |
| `Cliente` | `cliente` | Clientes / Fiado | Mantem historico e pendencias |
| `Comanda` | `comanda` | Comandas / Pagamentos / Fiado | Origem operacional do consumo |
| `ItemComanda` | `item_comanda` | Comandas | Snapshot de produto e preco |
| `Caixa` | `caixa` | Caixa Diario | Origem operacional de comandas e pagamentos |
| `Pagamento` | `pagamento` | Pagamentos / Fiado | Recebimentos reais |
| `MovimentoCaixa` | `movimento_caixa` | Caixa Diario | Abertura, reforco, sangria e ajuste |
| `MovimentoEstoque` | `movimento_estoque` | Estoque / Comandas | Movimentos manuais e automaticos |

## Relacionamentos principais

| Origem | Destino | Relacionamento |
|---|---|---|
| `CategoriaProduto` | `Produto` | Uma categoria possui varios produtos |
| `Produto` | `ItemComanda` | Um produto pode aparecer em varios itens |
| `Produto` | `MovimentoEstoque` | Um produto possui movimentos de estoque |
| `Produto` | `ProdutoComposicao` | Um produto composto possui varios componentes |
| `ProdutoComposicao` | `Produto` | Cada componente referencia um produto simples de estoque |
| `Cliente` | `Comanda` | Um cliente pode ter historico de comandas |
| `Caixa` | `Comanda` | Um caixa pode originar varias comandas |
| `Comanda` | `ItemComanda` | Uma comanda contem varios itens |
| `Comanda` | `Pagamento` | Uma comanda recebe pagamentos |
| `Caixa` | `Pagamento` | Um caixa registra pagamentos |
| `Caixa` | `MovimentoCaixa` | Um caixa possui movimentos financeiros |

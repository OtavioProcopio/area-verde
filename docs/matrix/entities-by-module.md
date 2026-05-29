# Entidades por Modulo

## Objetivo

Mapear as entidades reais em `app/core/domain/models.py`, seus campos
principais, relacionamentos e status operacional.

## ConfiguracaoSistema

Modulo principal: Configuracoes / Acesso. Status: Parcial. A tabela existe, mas
nao ha modulo operacional com endpoints.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `senha_acesso_hash` | String | Sim | Base futura para senha simples |
| `dias_para_alerta_fiado` | Integer | Sim | Parametro futuro de alerta/vencimento |
| `permitir_estoque_negativo` | Boolean | Sim | Parametro futuro; hoje a venda pode negativar estoque no MVP |
| `nome_bar` | String | Sim | Nome exibivel do bar |
| `observacao` | String | Nao | Observacao administrativa |
| `criado_em`, `atualizado_em` | DateTime | Sim | Auditoria simples |

## CategoriaProduto

Modulo principal: Produtos e Categorias. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `nome` | String | Sim | Nome unico entre categorias ativas |
| `ativo` | Boolean | Sim | Inativacao logica |
| `criado_em`, `atualizado_em` | DateTime | Sim | Auditoria simples |

Relacionamento: `CategoriaProduto 1 -> 0..* Produto`.

## Produto

Modulo principal: Produtos e Categorias / Estoque. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `categoria_id` | Long | Sim | FK para categoria |
| `nome` | String | Sim | Nome do produto |
| `preco_venda` | Decimal | Sim | Preco usado no snapshot do item |
| `controla_estoque` | Boolean | Sim | Define se gera movimentos automaticos |
| `unidade_estoque` | Enum | Sim | `UNIDADE` ou `ML` |
| `quantidade_estoque` | Decimal | Sim | Saldo atual |
| `quantidade_baixa_por_venda` | Decimal | Sim | Baixa aplicada por unidade vendida |
| `estoque_minimo` | Decimal | Sim | Base para estoque baixo |
| `ativo` | Boolean | Sim | Produto inativo nao deve ser vendido |
| `criado_em`, `atualizado_em` | DateTime | Sim | Auditoria simples |

Relacionamentos: `Produto 1 -> 0..* ItemComanda` e
`Produto 1 -> 0..* MovimentoEstoque`.

## Cliente

Modulo principal: Clientes / Fiado. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `nome` | String | Sim | Nome principal |
| `apelido` | String | Nao | Nome operacional |
| `telefone` | String | Nao | Usado para busca e duplicidade |
| `observacao` | String | Nao | Contexto operacional |
| `ativo` | Boolean | Sim | Cliente inativo nao gera novo fiado |
| `criado_em`, `atualizado_em` | DateTime | Sim | Auditoria simples |

Relacionamento: `Cliente 1 -> 0..* Comanda`. Pendencias de cliente inativo
permanecem visiveis e quitaveis.

## Comanda

Modulo principal: Comandas e Itens / Pagamentos / Fiado. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `caixa_origem_id` | Long | Nao | Caixa aberto no momento da criacao |
| `cliente_id` | Long | Nao | Vinculo opcional com cliente |
| `nome_cliente` | String | Sim | Nome operacional da comanda |
| `nome_cliente_snapshot` | String | Nao | Snapshot do cliente cadastrado |
| `status` | Enum | Sim | `ABERTA`, `FECHADA`, `PENDENTE`, `CANCELADA` |
| `total` | Decimal | Sim | Soma dos itens |
| `aberta_em` | DateTime | Sim | Data/hora de abertura |
| `fechada_em` | DateTime | Nao | Preenchido no pagamento/quitação |
| `cancelada_em` | DateTime | Nao | Preenchido no cancelamento |
| `pendente_em` | DateTime | Nao | Preenchido ao virar fiado |
| `vencimento_em` | Date | Nao | Vencimento da pendencia |
| `observacao` | String | Nao | Observacao operacional |
| `criado_em`, `atualizado_em` | DateTime | Sim | Auditoria simples |

Relacionamentos: `Comanda 1 -> 0..* ItemComanda`,
`Comanda 1 -> 0..* Pagamento`, `Cliente 1 -> 0..* Comanda` e
`Caixa 1 -> 0..* Comanda`.

## ItemComanda

Modulo principal: Comandas e Itens. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `comanda_id` | Long | Sim | FK para comanda |
| `produto_id` | Long | Nao | FK para produto; snapshot preserva historico |
| `nome_produto_snapshot` | String | Sim | Nome no momento da venda |
| `preco_unitario_snapshot` | Decimal | Sim | Preco no momento da venda |
| `quantidade` | Decimal | Sim | Quantidade consumida |
| `quantidade_baixada_estoque` | Decimal | Sim | Quanto foi baixado |
| `total_item` | Decimal | Sim | Total do item |
| `criado_em`, `atualizado_em` | DateTime | Sim | Auditoria simples |

## Caixa

Modulo principal: Caixa Diario. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `data` | Date | Sim | Dia operacional |
| `status` | Enum | Sim | `ABERTO` ou `FECHADO` |
| `valor_inicial` | Decimal | Sim | Dinheiro inicial |
| `dinheiro_esperado` | Decimal | Sim | Dinheiro fisico esperado |
| `dinheiro_informado` | Decimal | Nao | Valor contado no fechamento |
| `diferenca` | Decimal | Nao | Informado menos esperado |
| `aberto_em` | DateTime | Sim | Data/hora de abertura |
| `fechado_em` | DateTime | Nao | Preenchido somente ao fechar |
| `criado_em`, `atualizado_em` | DateTime | Sim | Auditoria simples |

Relacionamentos: `Caixa 1 -> 0..* MovimentoCaixa`,
`Caixa 1 -> 0..* Pagamento` e `Caixa 1 -> 0..* Comanda`.

## Pagamento

Modulo principal: Pagamentos e Fechamento / Fiado. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `caixa_id` | Long | Nao | Caixa aberto onde o recebimento foi registrado |
| `comanda_id` | Long | Sim | Comanda paga ou quitada |
| `forma_pagamento` | Enum | Sim | `DINHEIRO`, `PIX`, `CARTAO`, `FIADO` |
| `valor` | Decimal | Sim | Valor recebido |
| `observacao` | String | Nao | Observacao |
| `criado_em` | DateTime | Sim | Data/hora do recebimento |

Observacao: `FIADO` existe no enum, mas e bloqueado como pagamento recebido e
como forma de quitacao.

## MovimentoCaixa

Modulo principal: Caixa Diario. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `caixa_id` | Long | Sim | FK para caixa |
| `tipo` | Enum | Sim | `ABERTURA`, `SANGRIA`, `REFORCO`, `AJUSTE` |
| `valor` | Decimal | Sim | Valor movimentado |
| `observacao` | String | Nao | Observacao operacional |
| `criado_em` | DateTime | Sim | Data/hora |

## MovimentoEstoque

Modulo principal: Estoque / Comandas. Status: Implementado.

| Campo | Tipo conceitual | Obrigatorio | Observacao |
|---|---|---|---|
| `id` | Long | Sim | Identificador |
| `produto_id` | Long | Sim | FK para produto |
| `tipo` | Enum | Sim | `ENTRADA`, `SAIDA_VENDA`, `DEVOLUCAO_CANCELAMENTO`, `AJUSTE` |
| `quantidade` | Decimal | Sim | Quantidade movimentada |
| `estoque_antes` | Decimal | Sim | Saldo antes |
| `estoque_depois` | Decimal | Sim | Saldo depois |
| `origem` | Enum | Sim | `COMANDA`, `ENTRADA_MANUAL`, `AJUSTE_MANUAL`, `CANCELAMENTO` |
| `referencia_id` | Long | Nao | ID de origem operacional quando aplicavel |
| `observacao` | String | Nao | Observacao |
| `criado_em` | DateTime | Sim | Data/hora |

## Relatorios basicos

Modulo de consulta. Status: Implementado.

Nao cria tabelas nem migrations. Consolida dados existentes de `Comanda`,
`ItemComanda`, `Produto`, `Cliente`, `Pagamento`, `Caixa`, `MovimentoCaixa` e
`MovimentoEstoque`.

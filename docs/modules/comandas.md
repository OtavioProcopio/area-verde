# Módulo - Comandas e Itens

## Status

Implementado.

## Objetivo

Permitir abrir comandas por nome/apelido, lançar produtos consumidos, ajustar
quantidades, remover itens e cancelar comandas. Cada alteração recalcula o total
e integra automaticamente com o estoque quando o produto controla estoque.

O fechamento com pagamento é atendido pelo módulo de Pagamentos e Fechamento. O
módulo de Fiado / Pendências altera comandas abertas para `PENDENTE` quando o
consumo fica para pagamento futuro.

## Casos de uso atendidos

- Criar comanda por nome/apelido.
- Criar comanda com `clienteId` opcional.
- Vincular cliente a comanda aberta.
- Listar comandas e comandas abertas.
- Buscar comandas por nome, status e data.
- Consultar detalhes de uma comanda.
- Adicionar produto à comanda.
- Incrementar quantidade de item.
- Diminuir quantidade de item.
- Remover item da comanda.
- Cancelar comanda aberta.
- Recalcular total pela soma dos itens.
- Baixar e devolver estoque automaticamente.
- Registrar movimentos de estoque.

## Entidades envolvidas

- `Comanda`
- `ItemComanda`
- `Produto`
- `MovimentoEstoque`
- `StatusComanda`
- `Cliente`
- `TipoMovimentoEstoque`
- `OrigemMovimentoEstoque`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/comandas` | Cria comanda |
| `GET` | `/api/comandas` | Lista comandas com filtros |
| `GET` | `/api/comandas/abertas` | Lista comandas abertas |
| `GET` | `/api/comandas/{comanda_id}` | Consulta detalhes |
| `PATCH` | `/api/comandas/{comanda_id}/cliente` | Vincula cliente ativo |
| `POST` | `/api/comandas/{comanda_id}/itens` | Adiciona produto |
| `PATCH` | `/api/comandas/{comanda_id}/itens/{item_id}/incrementar` | Incrementa item |
| `PATCH` | `/api/comandas/{comanda_id}/itens/{item_id}/diminuir` | Diminui item |
| `DELETE` | `/api/comandas/{comanda_id}/itens/{item_id}` | Remove item |
| `PATCH` | `/api/comandas/{comanda_id}/cancelar` | Cancela comanda |

## Regras de negócio

- Toda comanda inicia com status `ABERTA` e total zero.
- Criar comanda exige caixa aberto. Erro: `caixa_aberto_nao_encontrado`.
- Ao criar, a comanda recebe `caixa_origem_id` com o caixa aberto.
- Comanda comum pode ser aberta apenas com `nomeCliente`.
- `clienteId` é opcional e não substitui a abertura rápida.
- Também é permitido informar `nomeCliente` e `clienteId` juntos.
- Quando `clienteId` é informado, o cliente deve existir e estar ativo.
- Se `clienteId` for informado sem `nomeCliente`, o sistema usa apelido ou nome do cliente.
- `nome_cliente_snapshot` registra o nome operacional do cliente cadastrado.
- Cliente só é obrigatório para fiado.
- Comanda sem cliente pode ser paga normalmente, mas não pode virar fiado.
- Status `PENDENTE` representa fiado ou valor a receber.
- Apenas comandas abertas podem receber itens, alterações ou cancelamento.
- O total da comanda é sempre derivado da soma dos itens.
- O cliente da API nunca envia total manualmente.
- Item guarda snapshot de nome e preço do produto.
- Adicionar produto já existente na comanda incrementa o item existente.
- Produto com controle de estoque gera baixa automática.
- Produto sem controle de estoque não gera movimento de estoque.
- Diminuir, remover ou cancelar devolve estoque proporcional.
- Venda pode deixar estoque negativo no MVP para não travar atendimento.
- Comanda cancelada permanece no histórico com seus itens e movimentos.
- Comanda fechada pelo módulo de pagamentos não pode receber novas alterações.

## Validações

- `nomeCliente` é obrigatório, não pode ser vazio e aceita até 160 caracteres.
- `nomeCliente` pode ser omitido quando `clienteId` for informado.
- Várias comandas abertas podem ter o mesmo nome/apelido.
- Cliente inexistente retorna `cliente_nao_encontrado`.
- Cliente inativo retorna `cliente_inativo`.
- Caixa aberto inexistente na criação retorna `caixa_aberto_nao_encontrado`.
- `quantidade` deve ser maior que zero.
- Produto deve existir. Erro: `produto_nao_encontrado`.
- Produto deve estar ativo. Erro: `produto_inativo`.
- Comanda deve estar aberta. Erro: `comanda_nao_aberta`.
- Item deve pertencer à comanda informada.

## Exemplos de request

Criar comanda:

```json
{
  "nomeCliente": "João",
  "observacao": "Cliente voltou mais tarde"
}
```

Criar comanda com cliente:

```json
{
  "clienteId": 1,
  "observacao": "Cliente cadastrado"
}
```

Criar comanda com nome operacional e cliente:

```json
{
  "nomeCliente": "João balcão",
  "clienteId": 1
}
```

Vincular cliente:

```json
{
  "clienteId": 1
}
```

Adicionar item:

```json
{
  "produtoId": 1,
  "quantidade": 3
}
```

Incrementar ou diminuir item:

```json
{
  "quantidade": 1
}
```

Se o corpo for omitido em incrementar/diminuir, a quantidade padrão é `1`.

Cancelar comanda:

```json
{
  "motivo": "Lançamento errado"
}
```

## Exemplos de response

Comanda criada:

```json
{
  "id": 1,
  "caixaOrigemId": 1,
  "clienteId": null,
  "nomeCliente": "João",
  "nomeClienteSnapshot": null,
  "status": "ABERTA",
  "total": 0.0,
  "abertaEm": "2026-05-26T18:40:00",
  "fechadaEm": null,
  "canceladaEm": null,
  "pendenteEm": null,
  "vencimentoEm": null,
  "observacao": "Cliente voltou mais tarde",
  "itens": []
}
```

Comanda com item:

```json
{
  "id": 1,
  "caixaOrigemId": 1,
  "clienteId": null,
  "nomeCliente": "João",
  "nomeClienteSnapshot": null,
  "status": "ABERTA",
  "total": 21.0,
  "abertaEm": "2026-05-26T18:40:00",
  "fechadaEm": null,
  "canceladaEm": null,
  "pendenteEm": null,
  "vencimentoEm": null,
  "observacao": null,
  "itens": [
    {
      "id": 10,
      "produtoId": 1,
      "nomeProduto": "Cerveja lata",
      "quantidade": 3.0,
      "precoUnitario": 7.0,
      "quantidadeBaixadaEstoque": 3.0,
      "totalItem": 21.0
    }
  ]
}
```

## Snapshot do produto

Ao lançar um item, o sistema grava:

- `nomeProduto`: nome do produto no momento da inclusão.
- `precoUnitario`: preço de venda no momento da inclusão.

Alterações futuras no cadastro do produto não mudam itens já lançados.

## Integração com estoque

Quando `controlaEstoque = true`, a comanda baixa estoque na adição ou incremento:

```text
quantidade_baixada = quantidade_baixa_por_venda * quantidade_vendida
```

Exemplos:

- 3 cervejas com baixa de 1 unidade por venda baixam 3 unidades.
- 2 doses com baixa de 50 ml por venda baixam 100 ml.

Cada baixa registra movimento:

- `tipo = SAIDA_VENDA`
- `origem = COMANDA`
- `referencia_id = id do item da comanda`

Produtos sem controle de estoque não geram movimento.

## Estoque negativo

No MVP, a venda não é bloqueada quando o estoque fica negativo. A operação é
permitida para não travar atendimento, o movimento é registrado e a consulta de
estoque negativo evidencia o problema operacional.

## Devolução de estoque

Diminuir ou remover item devolve a quantidade proporcional já baixada.

Cada devolução registra movimento:

- `tipo = DEVOLUCAO_CANCELAMENTO`
- `origem = COMANDA`

## Cancelamento

Cancelar uma comanda aberta:

- devolve o estoque de todos os itens controlados;
- registra movimentos de devolução com origem `CANCELAMENTO`;
- altera o status para `CANCELADA`;
- preenche `canceladaEm`;
- mantém a comanda, itens e movimentos para histórico.

## Fiado

O módulo de comandas não cria pagamento de fiado. Para pendência, use
`POST /api/comandas/{comanda_id}/fiado`. A comanda deve estar aberta, ter
consumo e possuir cliente cadastrado ativo.

## Testes relacionados

- `app/comandas_test.py`
- `app/relatorios_test.py`

## O que ainda não está incluso

- Relatórios avançados.
- Impressão.
- Integrações de pagamento.
- Autenticação complexa.
- Frontend.

## Próximo passo relacionado

- Configurações.

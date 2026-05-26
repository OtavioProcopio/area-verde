# Módulo de Comandas

## Objetivo

O módulo de Comandas e Itens da Comanda permite abrir atendimento por
nome/apelido, lançar produtos, ajustar quantidades, remover itens e cancelar
comandas. Cada alteração recalcula o total e integra automaticamente com o
estoque quando o produto controla estoque.

Este módulo não implementa fechamento com pagamento, fiado, caixa, relatórios,
impressão, integrações de pagamento, autenticação complexa ou frontend.

## Casos de uso atendidos

- Criar comanda por nome/apelido.
- Listar comandas e comandas abertas.
- Buscar comandas por nome, status e data.
- Consultar detalhes de uma comanda.
- Adicionar produto à comanda.
- Incrementar ou diminuir quantidade de item.
- Remover item da comanda.
- Cancelar comanda aberta.
- Recalcular total pela soma dos itens.
- Baixar e devolver estoque automaticamente.
- Registrar movimentos de estoque.

## Endpoints

### Criar comanda

`POST /api/comandas`

Request:

```json
{
  "nomeCliente": "João",
  "observacao": "Cliente voltou mais tarde"
}
```

Response:

```json
{
  "id": 1,
  "nomeCliente": "João",
  "status": "ABERTA",
  "total": 0.0,
  "abertaEm": "2026-05-26T18:40:00",
  "fechadaEm": null,
  "canceladaEm": null,
  "observacao": "Cliente voltou mais tarde",
  "itens": []
}
```

### Listar comandas

`GET /api/comandas`

Filtros opcionais:

- `status`: `ABERTA`, `CANCELADA`, `FECHADA` ou `PENDENTE`.
- `nome`: busca parcial por nome/apelido.
- `data`: data de abertura no formato `YYYY-MM-DD`.

### Listar abertas

`GET /api/comandas/abertas`

### Consultar detalhes

`GET /api/comandas/{comanda_id}`

### Adicionar item

`POST /api/comandas/{comanda_id}/itens`

Request:

```json
{
  "produtoId": 1,
  "quantidade": 3
}
```

### Incrementar item

`PATCH /api/comandas/{comanda_id}/itens/{item_id}/incrementar`

Request opcional:

```json
{
  "quantidade": 1
}
```

Se o corpo for omitido, o incremento padrão é `1`.

### Diminuir item

`PATCH /api/comandas/{comanda_id}/itens/{item_id}/diminuir`

Request opcional:

```json
{
  "quantidade": 1
}
```

Se a quantidade final chegar a zero, o item é removido da comanda.

### Remover item

`DELETE /api/comandas/{comanda_id}/itens/{item_id}`

### Cancelar comanda

`PATCH /api/comandas/{comanda_id}/cancelar`

Request opcional:

```json
{
  "motivo": "Lançamento errado"
}
```

## Regras de validação

- `nomeCliente` é obrigatório, não pode ser vazio e aceita até 160 caracteres.
- Várias comandas abertas podem ter o mesmo nome/apelido.
- `quantidade` deve ser maior que zero.
- Produto deve existir e estar ativo para ser adicionado ou incrementado.
- Apenas comandas com status `ABERTA` podem receber alterações ou cancelamento.
- O total nunca é recebido do cliente; sempre é derivado da soma dos itens.

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

## Próximos módulos

A ordem recomendada após este módulo é:

1. Pagamentos e fechamento de comanda.
2. Fiado / Pendências.
3. Caixa Diário.
4. Relatórios básicos.
5. Configurações.
6. Acesso / senha simples.
7. Release MVP para `main`.

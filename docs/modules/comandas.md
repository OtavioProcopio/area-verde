# Módulo - Comandas e Itens

## Status

Implementado.

## Objetivo

Permitir abrir comandas por nome/apelido, lançar produtos consumidos, alterar
quantidades, remover itens, cancelar comandas e integrar automaticamente com o
estoque.

## Casos de uso atendidos

- Criar comanda.
- Listar comandas.
- Listar comandas abertas.
- Buscar comandas por nome, status e data.
- Consultar detalhes de uma comanda.
- Adicionar produto à comanda.
- Incrementar quantidade de item.
- Diminuir quantidade de item.
- Remover item.
- Cancelar comanda.
- Recalcular total.
- Baixar e devolver estoque automaticamente.

## Entidades envolvidas

- `Comanda`
- `ItemComanda`
- `Produto`
- `MovimentoEstoque`
- `StatusComanda`
- `TipoMovimentoEstoque`
- `OrigemMovimentoEstoque`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/comandas` | Cria comanda |
| `GET` | `/api/comandas` | Lista comandas com filtros |
| `GET` | `/api/comandas/abertas` | Lista comandas abertas |
| `GET` | `/api/comandas/{comanda_id}` | Consulta detalhes |
| `POST` | `/api/comandas/{comanda_id}/itens` | Adiciona produto |
| `PATCH` | `/api/comandas/{comanda_id}/itens/{item_id}/incrementar` | Incrementa item |
| `PATCH` | `/api/comandas/{comanda_id}/itens/{item_id}/diminuir` | Diminui item |
| `DELETE` | `/api/comandas/{comanda_id}/itens/{item_id}` | Remove item |
| `PATCH` | `/api/comandas/{comanda_id}/cancelar` | Cancela comanda |

## Regras de negócio

- Toda comanda inicia com status `ABERTA` e total zero.
- Apenas comandas abertas podem ser alteradas ou canceladas.
- O total da comanda é sempre a soma dos itens.
- Item guarda snapshot de nome e preço do produto.
- Adicionar produto já existente na comanda incrementa o item existente.
- Produto com controle de estoque gera baixa automática.
- Diminuir, remover ou cancelar devolve estoque.
- Venda pode deixar estoque negativo no MVP.
- Comanda cancelada permanece no histórico.

## Validações

- `nomeCliente` é obrigatório e não pode ser vazio.
- Produto deve existir. Erro: `produto_nao_encontrado`.
- Produto deve estar ativo. Erro: `produto_inativo`.
- Quantidade deve ser maior que zero. Erro: `quantidade_invalida`.
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

Adicionar item:

```json
{
  "produtoId": 1,
  "quantidade": 3
}
```

Cancelar comanda:

```json
{
  "motivo": "Lançamento errado"
}
```

## Exemplos de response

```json
{
  "id": 1,
  "nomeCliente": "João",
  "status": "ABERTA",
  "total": 21.0,
  "abertaEm": "2026-05-26T18:40:00",
  "fechadaEm": null,
  "canceladaEm": null,
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

## Testes relacionados

- `app/comandas_test.py`

## O que ainda não está incluso

- Fechamento de comanda.
- Pagamento.
- Fiado.
- Caixa diário.
- Impressão.

## Próximo passo relacionado

- Pagamentos e Fechamento de Comanda.

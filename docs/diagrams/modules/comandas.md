# Diagrama do Modulo - Comandas e Itens

## Status

Implementado.

## Objetivo

Registrar consumo operacional, recalcular totais e movimentar estoque
automaticamente a partir dos itens de comanda.

```mermaid
flowchart LR
    Caixa[Caixa aberto]
    Cliente[Cliente opcional]
    Comanda[Comanda ABERTA]
    Item[ItemComanda]
    Produto[Produto]
    Composicao[ProdutoComposicao]
    Componente[Produto componente]
    Movimento[MovimentoEstoque]

    Criar["POST /api/comandas"]
    Vincular["PATCH /api/comandas/{id}/cliente"]
    Adicionar["POST /api/comandas/{id}/itens"]
    Incrementar["PATCH /api/comandas/{id}/itens/{item_id}/incrementar"]
    Diminuir["PATCH /api/comandas/{id}/itens/{item_id}/diminuir"]
    Remover["DELETE /api/comandas/{id}/itens/{item_id}"]
    Cancelar["PATCH /api/comandas/{id}/cancelar"]

    Caixa --> Criar
    Cliente --> Criar
    Criar --> Comanda
    Vincular --> Cliente
    Vincular --> Comanda
    Produto --> Adicionar
    Produto --> Composicao
    Composicao --> Componente
    Adicionar --> Item
    Incrementar --> Item
    Diminuir --> Item
    Remover --> Item
    Cancelar --> Comanda
    Item --> Comanda
    Adicionar --> Movimento
    Incrementar --> Movimento
    Diminuir --> Movimento
    Remover --> Movimento
    Cancelar --> Movimento
    Componente --> Movimento
```

## Entidades envolvidas

- `Comanda`
- `ItemComanda`
- `Cliente`
- `Caixa`
- `Produto`
- `ProdutoComposicao`
- `MovimentoEstoque`

## Casos de uso envolvidos

- Criar comanda rapida ou com cliente cadastrado.
- Exigir caixa aberto para nova comanda.
- Vincular cliente a comanda aberta.
- Adicionar, incrementar, diminuir e remover itens.
- Cancelar comanda.
- Baixar e devolver estoque automaticamente.
- Vender produto composto como item da comanda.
- Baixar e devolver componentes proporcionalmente.

# Diagrama do Modulo - Produtos e Categorias

## Status

Implementado.

## Objetivo

Manter o cadastro vendavel usado por estoque, comandas e relatorios.

```mermaid
flowchart LR
    Categoria[CategoriaProduto]
    Produto[Produto]
    Tipo[TipoProduto]
    Composicao[ProdutoComposicao]
    Componente[Produto componente]
    Unidade[UnidadeEstoque]
    Item[ItemComanda]
    Movimento[MovimentoEstoque]

    CatAPI["/api/categorias"]
    ProdAPI["/api/produtos"]
    CompAPI["/api/produtos/{produto_id}/composicao"]

    CatAPI --> Categoria
    Categoria --> Produto
    ProdAPI --> Produto
    Produto --> Tipo
    Produto --> Composicao
    Composicao --> Componente
    CompAPI --> Composicao
    Produto --> Unidade
    Produto --> Item
    Produto --> Movimento
```

## Entidades envolvidas

- `CategoriaProduto`
- `Produto`
- `TipoProduto`
- `ProdutoComposicao`
- `UnidadeEstoque`
- `ItemComanda`
- `MovimentoEstoque`

## Casos de uso envolvidos

- Cadastrar, listar, consultar, editar, ativar e inativar categorias.
- Cadastrar, listar, consultar, editar, ativar e inativar produtos.
- Configurar controle de estoque, unidade, baixa por venda e estoque minimo.
- Cadastrar produto composto.
- Gerenciar composicao de produto composto.

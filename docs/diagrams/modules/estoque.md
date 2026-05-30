# Diagrama do Modulo - Estoque

## Status

Implementado.

## Objetivo

Consultar saldo de produtos e registrar movimentos manuais ou automaticos de
estoque.

```mermaid
flowchart LR
    Produto[Produto]
    Componente[Componente de produto composto]
    Movimento[MovimentoEstoque]
    Comanda[Comanda/ItemComanda]
    RelatorioConsumo["GET /api/relatorios/estoque-consumido"]

    Consultar["GET /api/estoque"]
    Baixo["GET /api/estoque/baixo"]
    Negativo["GET /api/estoque/negativo"]
    Historico["GET /api/estoque/produtos/{produto_id}/movimentos"]
    Entrada["POST /api/estoque/produtos/{produto_id}/entrada"]
    Ajuste["POST /api/estoque/produtos/{produto_id}/ajuste"]
    BaixaVenda["Baixa automatica por venda"]
    BaixaComponente["Baixa automatica por componente"]
    Devolucao["Devolucao automatica por cancelamento/reducao"]
    DevolucaoComponente["Devolucao automatica de componente"]

    Produto --> Consultar
    Produto --> Baixo
    Produto --> Negativo
    Produto --> Entrada
    Produto --> Ajuste
    Entrada --> Movimento
    Ajuste --> Movimento
    Comanda --> BaixaVenda
    Comanda --> BaixaComponente
    Comanda --> Devolucao
    Comanda --> DevolucaoComponente
    BaixaVenda --> Movimento
    BaixaComponente --> Componente
    BaixaComponente --> Movimento
    Devolucao --> Movimento
    DevolucaoComponente --> Componente
    DevolucaoComponente --> Movimento
    Movimento --> Historico
    Movimento --> RelatorioConsumo
```

## Entidades envolvidas

- `Produto`
- `ProdutoComposicao`
- `MovimentoEstoque`
- `TipoMovimentoEstoque`
- `OrigemMovimentoEstoque`

## Casos de uso envolvidos

- Consultar estoque, baixo e negativo.
- Registrar entrada e ajuste manual.
- Consultar movimentos.
- Registrar baixa e devolucao automaticas via comanda.
- Registrar baixa e devolucao automaticas por componente de produto composto.
- Consultar consumo fisico de estoque por movimentos.

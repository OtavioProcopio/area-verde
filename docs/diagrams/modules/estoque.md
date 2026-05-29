# Diagrama do Modulo - Estoque

## Status

Implementado.

## Objetivo

Consultar saldo de produtos e registrar movimentos manuais ou automaticos de
estoque.

```mermaid
flowchart LR
    Produto[Produto]
    Movimento[MovimentoEstoque]
    Comanda[Comanda/ItemComanda]

    Consultar["GET /api/estoque"]
    Baixo["GET /api/estoque/baixo"]
    Negativo["GET /api/estoque/negativo"]
    Historico["GET /api/estoque/produtos/{produto_id}/movimentos"]
    Entrada["POST /api/estoque/produtos/{produto_id}/entrada"]
    Ajuste["POST /api/estoque/produtos/{produto_id}/ajuste"]
    BaixaVenda["Baixa automatica por venda"]
    Devolucao["Devolucao automatica por cancelamento/reducao"]

    Produto --> Consultar
    Produto --> Baixo
    Produto --> Negativo
    Produto --> Entrada
    Produto --> Ajuste
    Entrada --> Movimento
    Ajuste --> Movimento
    Comanda --> BaixaVenda
    Comanda --> Devolucao
    BaixaVenda --> Movimento
    Devolucao --> Movimento
    Movimento --> Historico
```

## Entidades envolvidas

- `Produto`
- `MovimentoEstoque`
- `TipoMovimentoEstoque`
- `OrigemMovimentoEstoque`

## Casos de uso envolvidos

- Consultar estoque, baixo e negativo.
- Registrar entrada e ajuste manual.
- Consultar movimentos.
- Registrar baixa e devolucao automaticas via comanda.

# Diagrama do Modulo - Relatorios

## Status

Pendente.

## Objetivo

Consolidar dados operacionais ja existentes em consultas de apoio a gestao.

```mermaid
flowchart LR
    Relatorios[Relatorios basicos]
    Comanda[Comanda]
    Item[ItemComanda]
    Produto[Produto]
    Cliente[Cliente]
    Pagamento[Pagamento]
    Caixa[Caixa]
    MovimentoCaixa[MovimentoCaixa]
    MovimentoEstoque[MovimentoEstoque]

    Diario["Relatorio diario"]
    PorCaixa["Relatorio por caixa"]
    PorForma["Relatorio por forma de pagamento"]
    MaisVendidos["Produtos mais vendidos"]
    Fiados["Relatorio de fiados"]
    Estoque["Relatorio de estoque"]
    Status["Comandas por status"]

    Comanda --> Relatorios
    Item --> Relatorios
    Produto --> Relatorios
    Cliente --> Relatorios
    Pagamento --> Relatorios
    Caixa --> Relatorios
    MovimentoCaixa --> Relatorios
    MovimentoEstoque --> Relatorios
    Relatorios --> Diario
    Relatorios --> PorCaixa
    Relatorios --> PorForma
    Relatorios --> MaisVendidos
    Relatorios --> Fiados
    Relatorios --> Estoque
    Relatorios --> Status
```

## Entidades envolvidas

- `Comanda`
- `ItemComanda`
- `Produto`
- `Cliente`
- `Pagamento`
- `Caixa`
- `MovimentoCaixa`
- `MovimentoEstoque`

## Endpoints envolvidos

A definir no modulo 8. Nenhum endpoint de relatorio existe hoje.

## Casos de uso previstos

- Gerar relatorio diario.
- Gerar relatorio por caixa.
- Gerar relatorio por forma de pagamento.
- Gerar relatorio de produtos mais vendidos.
- Gerar relatorio de fiados.
- Gerar relatorio de estoque.
- Gerar relatorio de comandas por status.

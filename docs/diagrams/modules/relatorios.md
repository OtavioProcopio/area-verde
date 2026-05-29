# Diagrama do Modulo - Relatorios

## Status

Implementado.

## Objetivo

Consolidar dados operacionais ja existentes em consultas de apoio a gestao.

```mermaid
flowchart LR
    Controller[RelatorioController]
    Service[RelatorioService]
    Repo[RelatorioRepository]

    Comanda[Comanda]
    Item[ItemComanda]
    Produto[Produto]
    Cliente[Cliente]
    Pagamento[Pagamento]
    Caixa[Caixa]
    MovimentoCaixa[MovimentoCaixa]

    Diario["GET /api/relatorios/diario"]
    PorCaixa["GET /api/relatorios/caixas/{caixa_id}"]
    MaisVendidos["GET /api/relatorios/produtos-mais-vendidos"]
    Fiados["GET /api/relatorios/fiados"]
    Estoque["GET /api/relatorios/estoque"]
    Status["GET /api/relatorios/comandas"]

    Diario --> Controller
    PorCaixa --> Controller
    MaisVendidos --> Controller
    Fiados --> Controller
    Estoque --> Controller
    Status --> Controller

    Controller --> Service
    Service --> Repo
    Repo --> Comanda
    Repo --> Item
    Repo --> Produto
    Repo --> Cliente
    Repo --> Pagamento
    Repo --> Caixa
    Repo --> MovimentoCaixa
```

## Entidades envolvidas

- `Comanda`
- `ItemComanda`
- `Produto`
- `Cliente`
- `Pagamento`
- `Caixa`
- `MovimentoCaixa`

## Endpoints envolvidos

- `GET /api/relatorios/diario`
- `GET /api/relatorios/caixas/{caixa_id}`
- `GET /api/relatorios/produtos-mais-vendidos`
- `GET /api/relatorios/fiados`
- `GET /api/relatorios/estoque`
- `GET /api/relatorios/comandas`

## Casos de uso implementados

- Gerar relatorio diario.
- Gerar relatorio por caixa.
- Gerar relatorio de produtos mais vendidos.
- Gerar relatorio de fiados.
- Gerar relatorio de estoque.
- Gerar relatorio de comandas por status.

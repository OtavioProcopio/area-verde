# Diagrama do Modulo - Caixa Diario

## Status

Implementado.

## Objetivo

Controlar abertura, movimentacoes fisicas, pagamentos vinculados e fechamento do
caixa operacional.

```mermaid
flowchart LR
    Caixa[Caixa]
    Movimento[MovimentoCaixa]
    Pagamento[Pagamento]
    Comanda[Comanda]

    Abrir["POST /api/caixas/abrir"]
    Aberto["GET /api/caixas/aberto"]
    Listar["GET /api/caixas"]
    Consultar["GET /api/caixas/{caixa_id}"]
    Reforco["POST /api/caixas/{caixa_id}/reforcos"]
    Sangria["POST /api/caixas/{caixa_id}/sangrias"]
    Fechar["POST /api/caixas/{caixa_id}/fechar"]

    Abrir --> Caixa
    Abrir --> Movimento
    Aberto --> Caixa
    Listar --> Caixa
    Consultar --> Caixa
    Reforco --> Movimento
    Sangria --> Movimento
    Movimento --> Caixa
    Pagamento --> Caixa
    Comanda --> Caixa
    Fechar --> Caixa
    Fechar --> Comanda
```

## Entidades envolvidas

- `Caixa`
- `MovimentoCaixa`
- `Pagamento`
- `Comanda`
- `StatusCaixa`
- `TipoMovimentoCaixa`

## Casos de uso envolvidos

- Abrir, consultar, listar e fechar caixa.
- Registrar reforco e sangria.
- Calcular dinheiro esperado e diferenca.
- Bloquear fechamento com comandas abertas.
- Permitir fechamento com comandas pendentes.

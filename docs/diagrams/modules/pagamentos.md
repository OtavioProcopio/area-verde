# Diagrama do Modulo - Pagamentos e Fechamento

## Status

Implementado.

## Objetivo

Fechar comandas abertas com recebimento real e vincular pagamentos ao caixa
aberto.

```mermaid
flowchart LR
    Comanda[Comanda ABERTA]
    Pagamento[Pagamento]
    Caixa[Caixa aberto]
    Fechada[Comanda FECHADA]

    Fechar["POST /api/comandas/{comanda_id}/fechar"]
    Listar["GET /api/comandas/{comanda_id}/pagamentos"]
    Bloqueio["Bloquear FIADO como pagamento recebido"]

    Comanda --> Fechar
    Caixa --> Fechar
    Fechar --> Bloqueio
    Fechar --> Pagamento
    Pagamento --> Caixa
    Fechar --> Fechada
    Fechada --> Listar
    Pagamento --> Listar
```

## Entidades envolvidas

- `Comanda`
- `Pagamento`
- `Caixa`
- `FormaPagamento`
- `StatusComanda`

## Casos de uso envolvidos

- Fechar comanda com DINHEIRO, PIX ou CARTAO.
- Listar pagamentos da comanda.
- Bloquear FIADO como pagamento recebido.
- Atualizar dinheiro esperado apenas quando a forma for DINHEIRO.

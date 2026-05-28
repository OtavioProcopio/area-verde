# Diagrama do Modulo - Fiado / Pendencias

## Status

Implementado.

## Objetivo

Transformar consumo nao recebido em pendencia rastreavel e permitir quitacao
posterior com pagamento real.

```mermaid
flowchart LR
    Cliente[Cliente ativo]
    ComandaAberta[Comanda ABERTA]
    Pendente[Comanda PENDENTE]
    Caixa[Caixa aberto]
    Pagamento[Pagamento]

    Marcar["POST /api/comandas/{comanda_id}/fiado"]
    Listar["GET /api/fiados"]
    Vencidos["GET /api/fiados/vencidos"]
    Consultar["GET /api/fiados/{comanda_id}"]
    Quitar["POST /api/fiados/{comanda_id}/quitar"]

    Cliente --> Marcar
    Caixa --> Marcar
    ComandaAberta --> Marcar
    Marcar --> Pendente
    Pendente --> Listar
    Pendente --> Vencidos
    Pendente --> Consultar
    Caixa --> Quitar
    Pendente --> Quitar
    Quitar --> Pagamento
    Quitar --> ComandaAberta
```

## Entidades envolvidas

- `Cliente`
- `Comanda`
- `Pagamento`
- `Caixa`
- `FormaPagamento`
- `StatusComanda`

## Casos de uso envolvidos

- Marcar comanda como fiado.
- Exigir cliente cadastrado e caixa aberto.
- Definir vencimento e listar vencidos.
- Quitar pendencia com DINHEIRO, PIX ou CARTAO.
- Manter pendencias de cliente inativo visiveis.

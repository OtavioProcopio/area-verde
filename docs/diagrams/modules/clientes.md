# Diagrama do Modulo - Clientes

## Status

Implementado.

## Objetivo

Manter cadastro simples de clientes para historico e fiado, sem bloquear a
criacao rapida de comandas por nome/apelido.

```mermaid
flowchart LR
    Cliente[Cliente]
    Comanda[Comanda]
    Pendencias["Pendencias do cliente"]

    Cadastrar["POST /api/clientes"]
    Listar["GET /api/clientes"]
    Consultar["GET /api/clientes/{cliente_id}"]
    Editar["PUT /api/clientes/{cliente_id}"]
    Ativar["PATCH /api/clientes/{cliente_id}/ativar"]
    Inativar["PATCH /api/clientes/{cliente_id}/inativar"]
    VerPendencias["GET /api/clientes/{cliente_id}/pendencias"]

    Cadastrar --> Cliente
    Listar --> Cliente
    Consultar --> Cliente
    Editar --> Cliente
    Ativar --> Cliente
    Inativar --> Cliente
    Cliente --> Comanda
    VerPendencias --> Pendencias
    Pendencias --> Comanda
```

## Entidades envolvidas

- `Cliente`
- `Comanda`

## Casos de uso envolvidos

- Cadastrar, listar, consultar, editar, ativar e inativar cliente.
- Validar duplicidade de cliente ativo por nome ou telefone normalizados.
- Consultar pendencias do cliente.
- Manter historico e pendencias de clientes inativos.

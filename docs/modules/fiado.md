# Módulo - Fiado / Pendências

## Status

Implementado.

## Objetivo

Controlar comandas deixadas para pagamento futuro. Uma comanda fiada fica com
status `PENDENTE`, representa valor a receber e não entra como dinheiro recebido
no caixa do dia.

## Diferença entre FIADO e pagamento recebido

`FormaPagamento.FIADO` não é pagamento. Ela representa a decisão operacional de
marcar a comanda como pendente. A quitação futura deve usar `DINHEIRO`, `PIX` ou
`CARTAO` e exige caixa aberto no dia do recebimento.

## Casos de uso atendidos

- Marcar comanda aberta como fiado.
- Exigir cliente cadastrado e ativo para fiado.
- Definir `vencimento_em` manual ou padrão de 7 dias.
- Listar pendências.
- Listar pendências vencidas.
- Consultar pendência por comanda.
- Quitar pendência.
- Registrar pagamento da quitação no caixa aberto.
- Somar dinheiro esperado apenas quando a quitação for em dinheiro.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/comandas/{comanda_id}/fiado` | Marca comanda como pendente |
| `GET` | `/api/fiados` | Lista pendências |
| `GET` | `/api/fiados/vencidos` | Lista pendências vencidas |
| `GET` | `/api/fiados/{comanda_id}` | Consulta pendência |
| `POST` | `/api/fiados/{comanda_id}/quitar` | Quita pendência |

## Requests

**POST /api/comandas/10/fiado**
```json
{
  "clienteId": 1,
  "vencimentoEm": "2026-06-03",
  "observacao": "Cliente pagará na próxima semana"
}
```

**POST /api/fiados/10/quitar**
```json
{
  "formaPagamento": "DINHEIRO",
  "valorPago": 80.00,
  "observacao": "Quitado no balcão"
}
```

## Responses

**GET /api/fiados**
```json
[
  {
    "comandaId": 10,
    "cliente": {
      "id": 1,
      "nome": "João da Oficina",
      "apelido": "João"
    },
    "nomeCliente": "João",
    "total": "80.00",
    "status": "PENDENTE",
    "abertaEm": "2026-05-27T18:00:00",
    "vencimentoEm": "2026-06-03",
    "vencida": false
  }
]
```

**POST /api/fiados/10/quitar**
```json
{
  "id": 10,
  "status": "FECHADA",
  "total": "80.00",
  "vencimentoEm": "2026-06-03",
  "fechadaEm": "2026-06-01T20:00:00",
  "pagamentos": [
    {
      "id": 5,
      "caixaId": 2,
      "comandaId": 10,
      "formaPagamento": "DINHEIRO",
      "valor": "80.00",
      "observacao": "Quitado no balcão",
      "criadoEm": "2026-06-01T20:00:00"
    }
  ]
}
```

## Regras de negócio

- Apenas comanda `ABERTA` pode virar fiado.
- Comanda deve ter itens e total maior que zero.
- Cliente cadastrado e ativo é obrigatório.
- Se a comanda já tiver cliente, `clienteId` pode ser omitido no request.
- Se `vencimentoEm` não for enviado, o padrão é hoje + 7 dias.
- Vencimento anterior à data atual é bloqueado.
- Marcar fiado não cria pagamento e não altera caixa.
- Quitar fiado exige caixa aberto.
- `FIADO` não pode quitar fiado.
- Pagamento em `DINHEIRO` soma em `dinheiro_esperado`.
- Pagamento em `PIX` ou `CARTAO` fica vinculado ao caixa sem alterar dinheiro físico.
- A quitação altera a comanda para `FECHADA` e mantém `vencimento_em` para histórico.

## Validações

- `cliente_obrigatorio_para_fiado`
- `cliente_nao_encontrado`
- `cliente_inativo`
- `comanda_nao_encontrada`
- `comanda_nao_aberta`
- `comanda_nao_pendente`
- `comanda_sem_consumo`
- `vencimento_invalido`
- `valor_pago_invalido`
- `fiado_nao_pode_quitar_fiado`
- `caixa_aberto_nao_encontrado`

## Testes relacionados

- `app/fiado_test.py`
- `app/clientes_test.py`
- `app/caixa_test.py`
- `app/pagamentos_test.py`

## Fora de escopo

- Pagamento parcial.
- Juros.
- Parcelamento.
- Limite de crédito.
- Cobrança automática.
- Integração Pix/cartão real.

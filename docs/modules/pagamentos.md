# Módulo - Pagamentos e Fechamento

## Status

Implementado.

## Objetivo

Permitir fechar comanda aberta com forma de pagamento à vista, registrar o valor
pago e vincular o pagamento ao caixa diário aberto. Neste MVP, o caixa precisa
estar aberto para registrar pagamentos.

## Casos de uso atendidos

- Fechar comanda aberta.
- Registrar forma de pagamento (DINHEIRO, PIX, CARTAO).
- Registrar valor pago e observação opcional.
- Vincular pagamento ao caixa aberto.
- Registrar pagamento parcial (valor menor que o saldo restante), deixando a comanda
  `PARCIALMENTE_PAGA` até um ou mais pagamentos completarem o total ajustado.
- Aceitar múltiplos pagamentos para a mesma comanda até o saldo restante zerar.
- Validar valor pago maior que zero e não superior ao saldo restante da comanda.
- Rejeitar `FIADO` como pagamento recebido.
- Rejeitar fechamento de comanda vazia (sem itens consumidos).
- Atualizar status da comanda para `PARCIALMENTE_PAGA` (saldo > 0) ou `FECHADA`
  (saldo == 0) a cada pagamento.
- Preencher `fechada_em` apenas quando o saldo restante zera.
- Listar pagamentos registrados para uma comanda.
- Bloquear fechamento duplicado.
- Bloquear alterações de itens após fechamento; bloquear itens novos assim que a
  comanda tiver pagamento parcial registrado (ver `docs/modules/comandas.md`).

## Entidades envolvidas

- `Comanda`
- `Pagamento`
- `Caixa`
- `FormaPagamento` (DINHEIRO, PIX, CARTAO, FIADO)
- `StatusComanda`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/comandas/{comanda_id}/fechar` | Fecha comanda e registra pagamento |
| `GET` | `/api/comandas/{comanda_id}/pagamentos` | Lista pagamentos da comanda |

## Regras de negócio

- Não é permitido fechar comanda sem itens consumidos.
- Comandas já fechadas não podem ser fechadas novamente.
- Não é permitido adicionar, incrementar, diminuir ou remover itens em comandas fechadas
  ou com pagamento parcial (`PARCIALMENTE_PAGA`).
- Fechamento é aceito para comanda `ABERTA` ou `PARCIALMENTE_PAGA`.
- O valor pago deve ser maior que zero e não pode ultrapassar o saldo restante
  (`totalAjustado - pagamentos já registrados`) da comanda.
- Se o pagamento não completar o saldo restante, a comanda fica `PARCIALMENTE_PAGA`
  (não fecha) e o saldo restante segue exposto na resposta; se completar, a comanda
  fica `FECHADA` e `fechadaEm` é preenchido.
- `totalAjustado`/`saldoRestante` já refletem acréscimos/descontos aplicados via
  `POST /api/comandas/{id}/ajustes` (ver `docs/modules/comandas.md`).
- `FIADO` não fecha comanda como pagamento recebido.
- FIADO não é pagamento. Fiado é tratado pelo módulo de Fiado / Pendências,
  onde a comanda vira `PENDENTE`.
- Quitação de fiado gera pagamento real no caixa atual.
- O pagamento exige caixa aberto.
- Pagamento em DINHEIRO soma o valor em `dinheiro_esperado` do caixa.
- Pagamentos em PIX e CARTAO ficam vinculados ao caixa, mas não alteram o dinheiro físico esperado.
- O fechamento não calcula troco no MVP.

## Validações

- Comanda deve existir. Erro: `comanda_nao_encontrada`.
- Comanda deve estar `ABERTA` ou `PARCIALMENTE_PAGA`. Erro: `comanda_nao_aberta`.
- Comanda deve ter consumo maior que zero. Erro: `comanda_sem_consumo`.
- `valorPago` deve ser maior que zero.
- `valorPago` não pode ultrapassar o saldo restante. Erro: `valor_pago_invalido`.
- `formaPagamento=FIADO` é bloqueada. Erro: `forma_pagamento_invalida`.
- Deve existir caixa aberto. Erro: `caixa_aberto_nao_encontrado`.
- `observacao` aceita até 500 caracteres.

## Exemplos de request

**POST /api/comandas/1/fechar**
```json
{
  "formaPagamento": "PIX",
  "valorPago": 100.50,
  "observacao": ""
}
```

**POST /api/comandas/1/fechar** (pagamento parcial)
```json
{
  "formaPagamento": "DINHEIRO",
  "valorPago": 60.00
}
```

## Exemplos de response

**POST /api/comandas/1/fechar**
```json
{
  "id": 1,
  "nomeCliente": "Maria",
  "status": "FECHADA",
  "total": "100.50",
  "abertaEm": "2026-05-26T18:30:00",
  "fechadaEm": "2026-05-26T19:10:00",
  "canceladaEm": null,
  "observacao": null,
  "pagamentos": [
    {
      "id": 10,
      "caixaId": 1,
      "comandaId": 1,
      "formaPagamento": "PIX",
      "valor": "100.50",
      "observacao": "",
      "criadoEm": "2026-05-26T19:10:00"
    }
  ],
  "totalAjustado": "100.50",
  "saldoRestante": "0.00"
}
```

**POST /api/comandas/1/fechar** (pagamento parcial, resposta com `PARCIALMENTE_PAGA`)
```json
{
  "id": 1,
  "nomeCliente": "Maria",
  "status": "PARCIALMENTE_PAGA",
  "total": "100.00",
  "abertaEm": "2026-05-26T18:30:00",
  "fechadaEm": null,
  "canceladaEm": null,
  "observacao": null,
  "pagamentos": [
    {
      "id": 9,
      "caixaId": 1,
      "comandaId": 1,
      "formaPagamento": "DINHEIRO",
      "valor": "60.00",
      "observacao": null,
      "criadoEm": "2026-05-26T19:05:00"
    }
  ],
  "totalAjustado": "100.00",
  "saldoRestante": "40.00"
}
```

**GET /api/comandas/1/pagamentos**
```json
[
  {
    "id": 10,
    "caixaId": 1,
    "comandaId": 1,
    "formaPagamento": "PIX",
    "valor": "100.50",
    "observacao": "",
    "criadoEm": "2026-05-26T19:10:00"
  }
]
```

## Testes relacionados

- `app/tests/core/application/use_cases/pagamentos_test.py`
- `app/tests/core/application/use_cases/relatorios_test.py`
- `app/tests/bdd/fechamento_comanda_avancado_test.py`

## O que ainda não está incluso

- Relatórios financeiros avançados.
- Troco.
- Integração real com Pix, TEF, cartão ou gateway.
- Frontend.
- Release ou tag.

## Próximo passo relacionado

- Configurações.

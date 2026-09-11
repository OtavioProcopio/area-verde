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
- Validar valor pago igual ao total consumido na comanda.
- Rejeitar `FIADO` como pagamento recebido.
- Rejeitar fechamento de comanda vazia (sem itens consumidos).
- Atualizar status da comanda para fechada.
- Preencher `fechada_em` no fechamento.
- Listar pagamentos registrados para uma comanda.
- Bloquear fechamento duplicado.
- Bloquear alterações de itens após fechamento.

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
- Não é permitido adicionar, incrementar, diminuir ou remover itens em comandas fechadas.
- O valor pago deve ser exatamente igual ao valor total de consumo da comanda.
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
- Comanda deve estar aberta. Erro: `comanda_nao_aberta`.
- Comanda deve ter consumo maior que zero. Erro: `comanda_sem_consumo`.
- `valorPago` deve ser maior que zero.
- `valorPago` deve ser igual ao total. Erro: `valor_pago_invalido`.
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
  ]
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

- `app/pagamentos_test.py`
- `app/relatorios_test.py`

## O que ainda não está incluso

- Relatórios financeiros avançados.
- Troco.
- Integração real com Pix, TEF, cartão ou gateway.
- Frontend.
- Release ou tag.

## Próximo passo relacionado

- Configurações.

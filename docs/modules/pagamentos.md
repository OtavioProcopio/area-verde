# Módulo - Pagamentos e Fechamento

## Status

Implementado.

## Objetivo

Permitir fechar comanda aberta com forma de pagamento à vista, registrar o valor
pago e preparar integração futura com caixa diário. Neste MVP, o caixa não é
obrigatório para registrar pagamentos.

## Casos de uso atendidos

- Fechar comanda aberta.
- Registrar forma de pagamento (DINHEIRO, PIX, CARTAO).
- Registrar valor pago e observação opcional.
- Validar valor pago igual ao total consumido na comanda.
- Rejeitar pagamentos com forma de pagamento FIADO (não implementado).
- Rejeitar fechamento de comanda vazia (sem itens consumidos).
- Atualizar status da comanda para fechada.
- Preencher `fechada_em` no fechamento.
- Listar pagamentos registrados para uma comanda.
- Bloquear fechamento duplicado.
- Bloquear alterações de itens após fechamento.

## Entidades envolvidas

- `Comanda`
- `Pagamento`
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
- FIADO não está disponível no momento.
- O pagamento não exige `caixa_id` enquanto o módulo de Caixa Diário estiver pendente.
- O fechamento não calcula troco no MVP.

## Validações

- Comanda deve existir. Erro: `comanda_nao_encontrada`.
- Comanda deve estar aberta. Erro: `comanda_nao_aberta`.
- Comanda deve ter consumo maior que zero. Erro: `comanda_sem_consumo`.
- `valorPago` deve ser maior que zero.
- `valorPago` deve ser igual ao total. Erro: `valor_pago_invalido`.
- `formaPagamento=FIADO` é bloqueada. Erro: `fiado_nao_implementado`.
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

## O que ainda não está incluso

- Fiado completo.
- Caixa Diário.
- Relatórios financeiros.
- Troco.
- Integração real com Pix, TEF, cartão ou gateway.
- Frontend.
- Release ou tag.

## Próximo passo relacionado

- Implementar Fiado / Pendências e depois integrar pagamentos ao Caixa Diário.

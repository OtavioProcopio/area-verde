# Módulo - Pagamentos e Fechamento

## Status

Implementado.

## Objetivo

Permitir fechar comanda com forma de pagamento, registrar valor pago e preparar
integração com caixa diário (Cenário A - caixa não obrigatório para pagamentos no momento).

## Casos de uso previstos

- Fechar comanda aberta.
- Registrar forma de pagamento (DINHEIRO, PIX, CARTAO).
- Validar total pago em relação ao total consumido na comanda.
- Rejeitar pagamentos com forma de pagamento FIADO (não implementado).
- Rejeitar fechamento de comanda vazia (sem itens consumidos).
- Atualizar status da comanda para fechada.

## Entidades previstas

- `Comanda`
- `Pagamento`
- `FormaPagamento` (DINHEIRO, PIX, CARTAO, FIADO)

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | /api/comandas/{comanda_id}/fechar | Fechamento e registro de pagamento |
| GET | /api/comandas/{comanda_id}/pagamentos | Lista de pagamentos de uma comanda |

## Regras de negócio

- Não é permitido fechar comanda sem itens consumidos.
- Comandas já fechadas não podem ser fechadas novamente.
- Não é permitido adicionar itens em comandas fechadas.
- O valor pago deve ser exatamente igual ou superior ao valor total de consumo da comanda.
- FIADO não está disponível no momento.

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
  "comandaId": 1,
  "status": "FECHADA",
  "totalConsumo": 100.50,
  "valorPago": 100.50,
  "troco": 0.0,
  "mensagem": "Comanda fechada com sucesso."
}
```

## Testes relacionados

- `app/pagamentos_test.py`

## O que ainda não está incluso

- Modulo Fiado.
- Caixa Diário restrito.

## Próximo passo relacionado

- Implementar módulo de Caixa e Fiado dependendo da decisão de negócio (Cenário B).

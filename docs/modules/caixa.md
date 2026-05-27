# Módulo - Caixa Diário

## Status

Implementado.

## Objetivo

Controlar abertura, movimentações e fechamento financeiro diário do bar,
mantendo pagamentos de comandas vinculados ao caixa aberto.

## Casos de uso atendidos

- Abrir caixa.
- Consultar caixa aberto.
- Listar caixas com filtros por status e data.
- Consultar caixa por ID.
- Registrar reforço.
- Registrar sangria.
- Fechar caixa.
- Calcular dinheiro esperado.
- Registrar dinheiro informado.
- Calcular diferença de fechamento.
- Vincular pagamentos ao caixa aberto.
- Bloquear fechamento quando ainda existirem comandas abertas.
- Permitir fechamento com comandas pendentes.

## Entidades envolvidas

- `Caixa`
- `MovimentoCaixa`
- `Pagamento`
- `StatusCaixa`
- `TipoMovimentoCaixa`
- `FormaPagamento`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/caixas/abrir` | Abre caixa diário |
| `GET` | `/api/caixas/aberto` | Consulta caixa aberto |
| `GET` | `/api/caixas` | Lista caixas |
| `GET` | `/api/caixas/{caixa_id}` | Consulta detalhes do caixa |
| `POST` | `/api/caixas/{caixa_id}/reforcos` | Registra reforço |
| `POST` | `/api/caixas/{caixa_id}/sangrias` | Registra sangria |
| `POST` | `/api/caixas/{caixa_id}/fechar` | Fecha caixa |

## Regras de negócio

- Só pode existir um caixa `ABERTO` por vez.
- A abertura cria movimento `ABERTURA`.
- `valorInicial` deve ser maior ou igual a zero.
- Ao abrir, `dinheiroEsperado` começa igual a `valorInicial`.
- Reforço exige caixa aberto, cria movimento `REFORCO` e soma em `dinheiroEsperado`.
- Sangria exige caixa aberto, cria movimento `SANGRIA` e subtrai de `dinheiroEsperado`.
- Sangria não pode deixar `dinheiroEsperado` negativo.
- Fechamento exige caixa aberto e dinheiro informado maior ou igual a zero.
- Fechamento bloqueia comandas `ABERTA`.
- Comandas `PENDENTE`, `FECHADA` e `CANCELADA` não bloqueiam fechamento.
- Diferença é calculada por `dinheiroInformado - dinheiroEsperado`.
- Caixa fechado não aceita reforço, sangria ou novo fechamento.
- Pagamento de comanda exige caixa aberto.
- Pagamento DINHEIRO soma em `dinheiroEsperado`.
- Pagamentos PIX e CARTAO ficam vinculados ao caixa, mas não alteram dinheiro físico esperado.
- FIADO não é entrada de caixa.
- Fiado gerado não soma no dinheiro esperado.
- Quitação futura entra no caixa aberto do dia em que foi paga.

## Validações

- Caixa aberto duplicado. Erro: `caixa_ja_aberto`.
- Caixa aberto inexistente na consulta. Erro: `caixa_aberto_nao_encontrado`.
- Caixa inexistente. Erro: `caixa_nao_encontrado`.
- Movimentação em caixa fechado. Erro: `caixa_fechado`.
- Sangria maior que dinheiro esperado. Erro: `sangria_invalida`.
- Comandas abertas no fechamento. Erro: `existem_comandas_abertas`.
- Valores negativos ou zero em reforço/sangria retornam validação de entrada.

## Exemplos de request

**POST /api/caixas/abrir**
```json
{
  "valorInicial": 100.00,
  "observacao": "Abertura do turno"
}
```

**POST /api/caixas/1/reforcos**
```json
{
  "valor": 50.00,
  "observacao": "Troco adicional"
}
```

**POST /api/caixas/1/sangrias**
```json
{
  "valor": 30.00,
  "observacao": "Retirada parcial"
}
```

**POST /api/caixas/1/fechar**
```json
{
  "dinheiroInformado": 248.00,
  "observacao": "Fechamento do turno"
}
```

Erro ao fechar com comanda aberta:

```json
{
  "code": "existem_comandas_abertas",
  "message": "Não é possível fechar o caixa com comandas abertas",
  "details": [
    {
      "id": 1,
      "nomeCliente": "João",
      "total": "80.00",
      "abertaEm": "2026-05-27T18:00:00"
    }
  ]
}
```

## Exemplos de response

**GET /api/caixas/1**
```json
{
  "id": 1,
  "data": "2026-05-27",
  "status": "ABERTO",
  "valorInicial": "100.00",
  "dinheiroEsperado": "150.00",
  "dinheiroInformado": null,
  "diferenca": null,
  "abertoEm": "2026-05-27T18:00:00",
  "fechadoEm": null,
  "pagamentos": [
    {
      "id": 10,
      "caixaId": 1,
      "comandaId": 5,
      "formaPagamento": "DINHEIRO",
      "valor": "50.00",
      "observacao": null,
      "criadoEm": "2026-05-27T18:30:00"
    }
  ],
  "movimentos": [
    {
      "id": 1,
      "caixaId": 1,
      "tipo": "ABERTURA",
      "valor": "100.00",
      "observacao": "Abertura do turno",
      "criadoEm": "2026-05-27T18:00:00"
    }
  ]
}
```

**POST /api/caixas/1/fechar**
```json
{
  "id": 1,
  "data": "2026-05-27",
  "status": "FECHADO",
  "valorInicial": "100.00",
  "dinheiroEsperado": "150.00",
  "dinheiroInformado": "148.00",
  "diferenca": "-2.00",
  "abertoEm": "2026-05-27T18:00:00",
  "fechadoEm": "2026-05-27T23:00:00",
  "pagamentos": [],
  "movimentos": [
    {
      "id": 1,
      "caixaId": 1,
      "tipo": "ABERTURA",
      "valor": "100.00",
      "observacao": "Abertura do turno",
      "criadoEm": "2026-05-27T18:00:00"
    }
  ]
}
```

## Testes relacionados

- `app/caixa_test.py`
- `app/pagamentos_test.py`
- `app/fiado_test.py`

## O que ainda não está incluso

- Relatórios financeiros.
- Dashboard.
- Frontend.
- Autenticação e permissões.
- Integração real com Pix, TEF, cartão ou gateway.
- Troco.
- Nota fiscal.
- Impressão.
- Release, tag ou deploy.

## Próximo passo relacionado

- Relatórios básicos.

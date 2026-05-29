# Módulo - Relatórios

## Status

Implementado.

## Objetivo

Expor consultas consolidadas para acompanhamento operacional e financeiro do
bar, sem alterar dados e sem criar dashboard visual.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/relatorios/diario` | Consolida caixa, vendas, pagamentos, comandas, fiados e estoque de um dia |
| `GET` | `/api/relatorios/caixas/{caixa_id}` | Consolida recebimentos, movimentos, comandas e produtos de um caixa |
| `GET` | `/api/relatorios/produtos-mais-vendidos` | Lista produtos mais vendidos no período |
| `GET` | `/api/relatorios/fiados` | Resume pendências, vencidos e quitados no período |
| `GET` | `/api/relatorios/estoque` | Lista produtos controlados com estoque baixo ou negativo |
| `GET` | `/api/relatorios/estoque-consumido` | Lista consumo liquido de estoque por produto movimentado |
| `GET` | `/api/relatorios/comandas` | Resume comandas por status e período |

## Query params

### Relatório diário

- `data`: opcional. Quando ausente, usa a data atual.

### Produtos mais vendidos

- `dataInicio`: opcional.
- `dataFim`: opcional.
- `limite`: opcional, padrão `10`, máximo `100`.

### Fiados

- `status`: `pendentes`, `vencidos`, `quitados` ou `todos`. Padrão `todos`.
  Quando `status=quitados`, a lista `pendencias` retorna comandas que viraram
  fiado e foram quitadas por pagamento real no período.
- `clienteId`: opcional.
- `dataInicio`: opcional.
- `dataFim`: opcional.

### Estoque

- `tipo`: `baixo`, `negativo` ou `todos`. Padrão `todos`.

### Estoque consumido

- `dataInicio`: opcional.
- `dataFim`: opcional.

### Comandas

- `dataInicio`: opcional.
- `dataFim`: opcional.
- `status`: opcional, aceita `ABERTA`, `FECHADA`, `PENDENTE` ou `CANCELADA`.

## Regras de cálculo

- Total vendido considera comandas `FECHADA` e `PENDENTE`.
- Comandas `ABERTA` aparecem em contagens operacionais, mas não entram como
  venda concluída.
- Comandas `CANCELADA` não entram em vendas nem em produtos mais vendidos.
- Total recebido vem de `Pagamento` com `DINHEIRO`, `PIX` ou `CARTAO`.
- `FIADO` não é pagamento recebido.
- Fiado gerado usa comandas com `pendente_em` e status `PENDENTE` ou `FECHADA`,
  para manter no relatório fiados quitados no mesmo dia/período.
- Fiado quitado usa pagamentos reais vinculados a comandas que possuem
  `pendente_em`.
- Relatório por caixa usa `pagamento.caixa_id` para recebimentos.
- Relatório por caixa usa `comanda.caixa_origem_id` para comandas originadas no
  caixa.
- Estoque baixo considera produto controlado com quantidade entre zero e o
  estoque mínimo.
- Estoque negativo considera produto controlado com quantidade menor que zero.
- Produtos mais vendidos usam `ItemComanda` e respondem o que o cliente comprou.
- Estoque consumido usa `MovimentoEstoque` e responde o que saiu fisicamente do
  estoque.
- Produto composto aparece como vendido em produtos mais vendidos.
- Componentes de produto composto aparecem como consumidos quando possuem
  movimentos de estoque.
- Devolucoes por diminuicao, remocao ou cancelamento abatem o consumo liquido.

## Validações

- `dataInicio` não pode ser maior que `dataFim`.
- `limite` deve estar entre `1` e `100`.
- `tipo` de estoque deve ser `baixo`, `negativo` ou `todos`.
- `status` de fiado deve ser `pendentes`, `vencidos`, `quitados` ou `todos`.
- Caixa inexistente retorna `caixa_nao_encontrado`.

## Exemplos de request

```http
GET /api/relatorios/diario?data=2026-05-28
GET /api/relatorios/caixas/1
GET /api/relatorios/produtos-mais-vendidos?dataInicio=2026-05-01&dataFim=2026-05-28&limite=10
GET /api/relatorios/fiados?status=vencidos
GET /api/relatorios/estoque?tipo=baixo
GET /api/relatorios/estoque-consumido?dataInicio=2026-05-01&dataFim=2026-05-28
GET /api/relatorios/comandas?status=FECHADA
```

## Venda x consumo de estoque

Os relatórios separam duas perguntas diferentes:

| Pergunta | Fonte | Exemplo com produto composto |
|---|---|---|
| O que o cliente comprou? | `ItemComanda` | `Dose Mista A+B` aparece como vendido |
| O que saiu fisicamente do estoque? | `MovimentoEstoque` | `Pinga A` e `Pinga B` aparecem como consumidos |

Assim, um produto composto vendido na comanda nao duplica os componentes em
produtos mais vendidos. Os componentes aparecem somente nos relatorios baseados
em movimentos de estoque.

## Exemplo de response - diário

```json
{
  "data": "2026-05-28",
  "caixa": null,
  "vendas": {
    "totalVendido": "0.00",
    "totalRecebido": "0.00",
    "totalFiadoGerado": "0.00",
    "totalPendenteAtual": "0.00"
  },
  "pagamentos": {
    "dinheiro": "0.00",
    "pix": "0.00",
    "cartao": "0.00"
  },
  "comandas": {
    "abertas": 0,
    "fechadas": 0,
    "pendentes": 0,
    "canceladas": 0
  },
  "fiados": {
    "geradosNoDia": "0.00",
    "quitadosNoDia": "0.00",
    "pendentesAtuais": "0.00",
    "vencidosAtuais": "0.00"
  },
  "estoque": {
    "produtosComEstoqueBaixo": 0,
    "produtosComEstoqueNegativo": 0
  }
}
```

## Testes relacionados

- `app/relatorios_test.py`
- Regressão: `app/produtos_categorias_test.py`, `app/estoque_test.py`,
  `app/comandas_test.py`, `app/pagamentos_test.py`, `app/caixa_test.py`,
  `app/clientes_test.py` e `app/fiado_test.py`.

## O que ainda não está incluso

- Dashboard visual.
- Exportação PDF, Excel ou CSV.
- Envio por e-mail.
- Agendamento de relatórios.
- BI avançado.
- Autenticação ou permissões.

## Próximo passo relacionado

- Configurações.

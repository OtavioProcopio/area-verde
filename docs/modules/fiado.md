# Módulo - Fiado / Pendências

## Status

Implementado.

## Objetivo

Controlar comandas deixadas para pagamento futuro. Uma comanda fiada fica com
status `PENDENTE`, representa valor a receber e não entra como dinheiro recebido
no caixa do dia.

## Diferença entre FIADO e pagamento recebido

`FormaPagamento.FIADO` não é pagamento. Ela representa a decisão operacional de
marcar a comanda como pendente dentro de um caixa aberto. A quitação futura deve
usar `DINHEIRO`, `PIX` ou `CARTAO` e exige caixa aberto no dia do recebimento.

## Casos de uso atendidos

- Marcar comanda aberta como fiado.
- Lançar fiado avulso para um cliente, sem depender de comanda, com data de origem
  retroativa (migração de dívida anterior ao sistema).
- Exigir cliente cadastrado e ativo para fiado.
- Exigir caixa aberto para marcar fiado a partir de uma comanda.
- Definir `vencimento_em` manual ou pelo padrão configurado do sistema.
- Registrar `pendente_em`.
- Preservar `caixa_origem_id` da comanda.
- Listar pendências.
- Listar pendências vencidas.
- Consultar pendência por comanda.
- Quitar pendência.
- Registrar pagamento da quitação no caixa aberto.
- Somar dinheiro esperado apenas quando a quitação for em dinheiro.
- Manter pendências de cliente inativo visíveis.

## Entidades envolvidas

- `Cliente`
- `Comanda`
- `Pagamento`
- `Caixa`
- `FormaPagamento`
- `StatusComanda`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/comandas/{comanda_id}/fiado` | Marca comanda como pendente |
| `POST` | `/api/fiados/avulso` | Lança fiado avulso para um cliente, sem comanda |
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

**POST /api/fiados/avulso**
```json
{
  "clienteId": 1,
  "valor": 150.00,
  "dataOrigem": "2026-08-01",
  "vencimentoEm": "2026-09-30",
  "observacao": "Saldo migrado da caderneta de papel"
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
    "nomeCliente": "Balcão",
    "nomeComanda": "Balcão",
    "nomeExibicao": "João",
    "total": "80.00",
    "status": "PENDENTE",
    "abertaEm": "2026-05-27T18:00:00",
    "pendenteEm": "2026-05-27T20:30:00",
    "vencimentoEm": "2026-06-03",
    "vencida": false
  }
]
```

**POST /api/fiados/avulso**
```json
{
  "comandaId": 11,
  "caixaOrigemId": null,
  "cliente": {
    "id": 1,
    "nome": "João da Oficina",
    "apelido": "João"
  },
  "nomeCliente": "João",
  "nomeComanda": "João",
  "nomeExibicao": "João",
  "total": "150.00",
  "status": "PENDENTE",
  "abertaEm": "2026-08-01T00:00:00",
  "pendenteEm": "2026-08-01T00:00:00",
  "vencimentoEm": "2026-09-30",
  "vencida": false,
  "fechadaEm": null,
  "canceladaEm": null,
  "observacao": "Saldo migrado da caderneta de papel",
  "itens": [],
  "pagamentos": []
}
```

**POST /api/fiados/10/quitar**
```json
{
  "id": 10,
  "status": "FECHADA",
  "total": "80.00",
  "pendenteEm": "2026-05-27T20:30:00",
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
- Deve existir caixa aberto para marcar fiado.
- Comanda deve ter itens e total maior que zero.
- Cliente cadastrado e ativo é obrigatório.
- Se a comanda já tiver cliente, `clienteId` pode ser omitido no request.
- Se `vencimentoEm` não for enviado, o padrão é hoje + `dias_para_alerta_fiado`
  da configuração atual. Sem configuração persistida, o fallback é 7 dias.
- Vencimento anterior à data atual é bloqueado.
- `pendente_em` recebe a data e hora em que a comanda virou `PENDENTE`.
- `caixa_origem_id` identifica o caixa em que a comanda foi aberta.
- Marcar fiado não cria pagamento e não altera caixa.
- Quitar fiado exige caixa aberto.
- Quitação continua permitida mesmo se o cliente foi inativado após a pendência.
- `FIADO` não pode quitar fiado.
- Pagamento em `DINHEIRO` soma em `dinheiro_esperado`.
- Pagamento em `PIX` ou `CARTAO` fica vinculado ao caixa sem alterar dinheiro físico.
- A quitação altera a comanda para `FECHADA` e mantém `vencimento_em` para histórico.
- A quitação não altera `pendente_em`.
- Fiado avulso não exige comanda nem caixa aberto: é um registro histórico, para migrar
  dívida de cliente anterior ao uso do sistema (ex.: caderneta de papel).
- Fiado avulso exige cliente cadastrado e ativo, valor devido maior que zero e data de
  origem — que pode ser qualquer data igual ou anterior a hoje, sem limite mínimo.
- Data de origem no futuro é bloqueada.
- No fiado avulso, `pendente_em` e `aberta_em` recebem a data de origem informada (não o
  instante do lançamento no sistema).
- No fiado avulso, `vencimento_em` segue a mesma regra do fiado por comanda: manual ou
  padrão do sistema quando omitido.
- Fiado avulso não cria itens (`itens` sempre vazio) nem movimenta estoque.
- Fiado avulso aparece nas mesmas listagens, consultas e no mesmo fluxo de quitação do
  fiado por comanda, sem endpoint nem histórico separado.

## Validações

- `cliente_obrigatorio_para_fiado`
- `cliente_nao_encontrado`
- `cliente_inativo`
- `data_origem_invalida`
- `valor_devido_invalido`
- `comanda_nao_encontrada`
- `comanda_nao_aberta`
- `comanda_nao_pendente`
- `comanda_sem_consumo`
- `vencimento_invalido`
- `valor_pago_invalido`
- `fiado_nao_pode_quitar_fiado`
- `caixa_aberto_nao_encontrado`

## Testes relacionados

- `app/tests/core/application/use_cases/fiado_test.py`
- `app/tests/core/application/use_cases/clientes_test.py`
- `app/tests/core/application/use_cases/caixa_test.py`
- `app/tests/core/application/use_cases/pagamentos_test.py`
- `app/tests/core/application/use_cases/relatorios_test.py`

## Fora de escopo

- Pagamento parcial.
- Juros.
- Parcelamento.
- Limite de crédito.
- Cobrança automática.
- Integração Pix/cartão real.

## Próximo passo relacionado

- Frontend operacional.

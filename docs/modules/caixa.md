# Módulo - Caixa Diário

## Status

Pendente.

## Objetivo

Controlar abertura, movimentações e fechamento financeiro diário do bar.

Pagamentos de comanda já são registrados sem `caixa_id` obrigatório. Este módulo
deverá definir como esses pagamentos serão vinculados ao caixa diário.

## Casos de uso previstos

- Abrir caixa.
- Registrar pagamentos.
- Registrar sangria.
- Registrar reforço.
- Fechar caixa.
- Calcular dinheiro esperado e diferença.

## Entidades previstas

- `Caixa`
- `MovimentoCaixa`
- `Pagamento`
- `StatusCaixa`
- `TipoMovimentoCaixa`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| A definir | A definir | Operações de caixa |

## Regras de negócio

- Ainda não implementado.

## Validações

- A definir durante implementação.

## Exemplos de request

Pendente.

## Exemplos de response

Pendente.

## Testes relacionados

- A criar.

## O que ainda não está incluso

- Todo o módulo está pendente.

## Próximo passo relacionado

- Implementar após a definição de Fiado / Pendências e vínculo de pagamentos ao caixa.

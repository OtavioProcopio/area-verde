# Módulo - Fiado / Pendências

## Status

Pendente.

## Objetivo

Controlar comandas ou saldos deixados para pagamento futuro.

No estado atual do MVP, `FormaPagamento.FIADO` existe no domínio, mas o
fechamento de comanda rejeita essa forma com o erro `fiado_nao_implementado`.

## Casos de uso previstos

- Marcar comanda como pendente/fiado.
- Listar pendências.
- Identificar pendências vencidas.
- Registrar quitação futura.

## Entidades previstas

- `Comanda`
- `Pagamento`
- `FormaPagamento`
- `ConfiguracaoSistema`

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| A definir | A definir | Gestão de fiado |

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

- Implementar a partir dos fluxos de Pagamentos, Fechamento e Caixa Diário.

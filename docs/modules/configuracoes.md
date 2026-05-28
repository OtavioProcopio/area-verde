# Módulo - Configurações

## Status

Pendente.

## Objetivo

Permitir configurar parâmetros operacionais simples do sistema.

## Casos de uso previstos

- Configurar nome do bar.
- Configurar dias para vencimento/alerta de fiado.
- Configurar permissão de estoque negativo.
- Configurar senha simples de acesso.

## Entidades envolvidas

- `ConfiguracaoSistema`

Observação: a entidade existe em `models.py`, mas não há controller, service
operacional ou endpoints para gestão de configurações nesta versão.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| A definir | A definir | Gestão de configurações |

## Regras de negócio

- Ainda não implementado como módulo completo.
- O módulo de Fiado / Pendências usa prazo padrão seguro de 7 dias para
  vencimento automático quando o request não informa `vencimentoEm`.

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

- Implementar antes de release MVP, se houver necessidade operacional.

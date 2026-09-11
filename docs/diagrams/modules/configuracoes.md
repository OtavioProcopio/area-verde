# Diagrama do Modulo - Configuracoes

## Status

Pendente.

## Objetivo

Futuramente parametrizar comportamento operacional simples do MVP.

```mermaid
flowchart LR
    Configuracao[ConfiguracaoSistema]
    NomeBar["Nome do bar"]
    DiasFiado["Dias para vencimento/alerta de fiado"]
    EstoqueNegativo["Permissao de estoque negativo"]
    Senha["Senha simples"]

    Configuracao --> NomeBar
    Configuracao --> DiasFiado
    Configuracao --> EstoqueNegativo
    Configuracao --> Senha
```

## Entidades envolvidas

- `ConfiguracaoSistema`

## Endpoints envolvidos

A definir. Nao ha endpoints reais de configuracao hoje.

## Casos de uso previstos

- Configurar nome do bar.
- Configurar dias para vencimento/alerta de fiado.
- Configurar permissao de estoque negativo.
- Configurar senha simples.

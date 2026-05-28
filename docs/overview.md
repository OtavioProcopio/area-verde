# Visão Geral - Area Verde API

## O que é

O Area Verde API é uma API para o MVP de controle operacional de um bar. O
sistema organiza o cadastro de produtos, controle de estoque, clientes,
comandas, pagamentos, fiado e caixa diário. Relatórios seguem como próximo
módulo planejado.

## Problema que resolve

O objetivo é reduzir controle manual e perda de rastreabilidade na operação do
bar. A API registra produtos vendidos, calcula total de comanda, fecha a venda
com forma de pagamento, controla pendências de clientes, vincula pagamentos ao
caixa aberto e mantém movimentações de estoque para que a equipe acompanhe
consumo, ajustes e divergências.

## Fluxo operacional

O fluxo operacional começa no cadastro de categorias e produtos. Produtos podem
controlar estoque por unidade ou por medida fracionada, como ml. Depois, o
estoque recebe entradas ou ajustes manuais. Na operação de atendimento, o caixa
do turno é aberto antes de qualquer nova comanda. A comanda é aberta por
nome/apelido ou cliente cadastrado, recebe itens e depois é resolvida como paga,
pendente/fiado ou cancelada. O caixa só fecha quando não restarem comandas
abertas.

## Fluxo atual implementado

```text
Produto -> Estoque -> Caixa -> Cliente -> Comanda -> Item -> Pagamento/Fiado
```

- Produto define preço, categoria e regra de baixa.
- Estoque registra entradas, ajustes e histórico.
- Comanda agrupa itens consumidos por cliente/apelido.
- Item mantém snapshot de nome e preço do produto.
- Movimentação de estoque registra baixa ou devolução.
- Caixa registra abertura, reforços, sangrias, pagamentos e fechamento.
- Pagamento registra forma, valor, observação e caixa vinculado.
- Fechamento altera a comanda para `FECHADA` e preenche `fechada_em`.
- Cliente pode ser vinculado opcionalmente à comanda.
- Comanda nova exige caixa aberto e grava `caixa_origem_id`.
- Fiado exige caixa aberto, altera a comanda para `PENDENTE`, define
  `pendente_em` e vencimento.
- Quitação de fiado registra pagamento real no caixa aberto do dia.
- Caixa não fecha com comandas `ABERTA`; pode fechar com `PENDENTE`.

## Fluxo futuro

```text
Relatórios
```

Após clientes, fiado, pagamentos e caixa, o próximo passo é expor relatórios
operacionais e financeiros básicos.

## Ordem do MVP

Implementado:

1. Produtos e Categorias
2. Estoque
3. Comandas e Itens
4. Pagamentos e Fechamento de Comanda
5. Caixa Diário
6. Clientes
7. Fiado / Pendências

Próximo:

8. Relatórios básicos

Depois:

9. Configurações
10. Acesso / Senha
11. Release MVP
12. Frontend operacional

## Documentos de referencia

- [Matriz funcional](matrix/functional-coverage.md)
- [Endpoints por modulo](matrix/endpoints-by-module.md)
- [Entidades por modulo](matrix/entities-by-module.md)
- [Testes por modulo](matrix/tests-by-module.md)
- [Pendencias e lacunas](matrix/pending-gaps.md)

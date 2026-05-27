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
do turno é aberto, uma comanda é aberta por nome/apelido, recebe itens e depois
é resolvida como paga, pendente/fiado ou cancelada.

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
- Fiado altera a comanda para `PENDENTE` e define vencimento.
- Quitação de fiado registra pagamento real no caixa aberto do dia.
- Caixa não fecha com comandas `ABERTA`; pode fechar com `PENDENTE`.

## Fluxo futuro

```text
Relatórios
```

Após clientes, fiado, pagamentos e caixa, o próximo passo é expor relatórios
operacionais e financeiros básicos.

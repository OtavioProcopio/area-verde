# Visão Geral - Area Verde API

## O que é

O Area Verde API é uma API para o MVP de controle operacional de um bar. O
sistema organiza o cadastro de produtos, controle de estoque, comandas e
fechamento com pagamento. Fiado completo, caixa diário e relatórios seguem como
módulos planejados.

## Problema que resolve

O objetivo é reduzir controle manual e perda de rastreabilidade na operação do
bar. A API registra produtos vendidos, calcula total de comanda, fecha a venda
com forma de pagamento e mantém movimentações de estoque para que a equipe
acompanhe consumo, ajustes e divergências.

## Fluxo operacional

O fluxo operacional começa no cadastro de categorias e produtos. Produtos podem
controlar estoque por unidade ou por medida fracionada, como ml. Depois, o
estoque recebe entradas ou ajustes manuais. Na operação de atendimento, uma
comanda é aberta por nome/apelido, recebe itens e depois é fechada com pagamento
à vista.

## Fluxo atual implementado

```text
Produto -> Estoque -> Comanda -> Item -> Pagamento -> Fechamento
```

- Produto define preço, categoria e regra de baixa.
- Estoque registra entradas, ajustes e histórico.
- Comanda agrupa itens consumidos por cliente/apelido.
- Item mantém snapshot de nome e preço do produto.
- Movimentação de estoque registra baixa ou devolução.
- Pagamento registra forma, valor e observação.
- Fechamento altera a comanda para `FECHADA` e preenche `fechada_em`.

## Fluxo futuro

```text
Fiado -> Caixa -> Relatórios
```

Após pagamentos, os próximos passos são tratar fiado completo, integrar os
pagamentos ao caixa diário e expor relatórios operacionais.

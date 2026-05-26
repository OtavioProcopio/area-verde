# Visão Geral - Area Verde API

## O que é

O Area Verde API é uma API para o MVP de controle operacional de um bar. O
sistema organiza o cadastro de produtos, controle de estoque, comandas e, nos
próximos módulos, fechamento financeiro, fiado, caixa diário e relatórios.

## Problema que resolve

O objetivo é reduzir controle manual e perda de rastreabilidade na operação do
bar. A API registra produtos vendidos, calcula total de comanda e mantém
movimentações de estoque para que a equipe acompanhe consumo, ajustes e
divergências.

## Fluxo operacional

O fluxo operacional começa no cadastro de categorias e produtos. Produtos podem
controlar estoque por unidade ou por medida fracionada, como ml. Depois, o
estoque recebe entradas ou ajustes manuais. Na operação de atendimento, uma
comanda é aberta por nome/apelido e recebe itens.

## Fluxo atual implementado

```text
Produto -> Estoque -> Comanda -> Item -> Movimentação de estoque
```

- Produto define preço, categoria e regra de baixa.
- Estoque registra entradas, ajustes e histórico.
- Comanda agrupa itens consumidos por cliente/apelido.
- Item mantém snapshot de nome e preço do produto.
- Movimentação de estoque registra baixa ou devolução.

## Fluxo futuro

```text
Pagamento -> Fiado -> Caixa -> Relatórios
```

Após comandas, o próximo passo é fechar a comanda com forma de pagamento ou
marcar pendência/fiado. Em seguida, os pagamentos alimentarão o caixa diário e
os relatórios operacionais.

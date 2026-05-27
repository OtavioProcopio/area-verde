# Visão Geral - Area Verde API

## O que é

O Area Verde API é uma API para o MVP de controle operacional de um bar. O
sistema organiza o cadastro de produtos, controle de estoque, comandas,
fechamento com pagamento e caixa diário. Fiado completo e relatórios seguem como
módulos planejados.

## Problema que resolve

O objetivo é reduzir controle manual e perda de rastreabilidade na operação do
bar. A API registra produtos vendidos, calcula total de comanda, fecha a venda
com forma de pagamento, vincula pagamentos ao caixa aberto e mantém
movimentações de estoque para que a equipe acompanhe consumo, ajustes e
divergências.

## Fluxo operacional

O fluxo operacional começa no cadastro de categorias e produtos. Produtos podem
controlar estoque por unidade ou por medida fracionada, como ml. Depois, o
estoque recebe entradas ou ajustes manuais. Na operação de atendimento, o caixa
do turno é aberto, uma comanda é aberta por nome/apelido, recebe itens e depois
é fechada com pagamento vinculado ao caixa diário.

## Fluxo atual implementado

```text
Produto -> Estoque -> Caixa -> Comanda -> Item -> Pagamento -> Fechamento
```

- Produto define preço, categoria e regra de baixa.
- Estoque registra entradas, ajustes e histórico.
- Comanda agrupa itens consumidos por cliente/apelido.
- Item mantém snapshot de nome e preço do produto.
- Movimentação de estoque registra baixa ou devolução.
- Caixa registra abertura, reforços, sangrias, pagamentos e fechamento.
- Pagamento registra forma, valor, observação e caixa vinculado.
- Fechamento altera a comanda para `FECHADA` e preenche `fechada_em`.

## Fluxo futuro

```text
Fiado -> Relatórios
```

Após caixa diário, os próximos passos são tratar fiado completo e expor
relatórios operacionais.

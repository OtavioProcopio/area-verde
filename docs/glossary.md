# Glossário do Domínio

## Comanda

Registro de atendimento aberto por nome/apelido. Agrupa itens consumidos e
mantém total calculado.

## Item de Comanda

Produto lançado em uma comanda, com quantidade, total e snapshot de nome e preço
do produto no momento da venda.

## Produto

Item vendável pelo bar. Possui preço, categoria e configuração de controle de
estoque.

## Categoria

Agrupamento de produtos, como cervejas, doses, refrigerantes ou salgados.

## Estoque

Quantidade operacional disponível de produtos que controlam estoque.

## Movimento de Estoque

Registro histórico de entrada, ajuste, baixa por venda ou devolução.

## Baixa de Estoque

Redução automática ou manual da quantidade em estoque.

## Devolução de Estoque

Retorno de quantidade ao estoque, normalmente por remoção, redução de item ou
cancelamento.

## Fiado

Comanda ou saldo deixado pendente para pagamento futuro.

## Pagamento

Registro financeiro associado a uma comanda fechada. No MVP, aceita DINHEIRO,
PIX e CARTAO, e exige valor igual ao total da comanda.

## Forma de Pagamento

Meio usado para liquidar a comanda. `FIADO` existe no enum do domínio, mas fica
bloqueado até o módulo de pendências ser implementado.

## Caixa Diário

Controle financeiro do dia, reunindo abertura, pagamentos, sangrias, reforços e
fechamento.

## Sangria

Retirada de dinheiro do caixa durante o expediente.

## Reforço

Entrada adicional de dinheiro no caixa durante o expediente.

# Especificação — Fechamento avançado de comanda: pagamento parcial e acréscimo/desconto

> Descreve **o quê** e **por quê**. Não descreve como implementar: sem nome de biblioteca,
> sem esquema de banco, sem assinatura de função.

## Problema

Hoje o fechamento de comanda (`PagamentoService.fechar_comanda`) e a quitação de fiado
(`FiadoService.quitar`) só aceitam pagamento do valor total exato da comanda de uma só vez.
Não existe conceito de saldo restante: um cliente que paga parte da conta na hora e deixa o
resto fiado, ou que paga em duas etapas, não tem como ter isso registrado corretamente no
sistema hoje — a operação é simplesmente rejeitada. O frontend (`CartPanel.tsx`) já calcula e
exibe "Recebido"/"Restante", mas o backend rejeita qualquer valor que não seja exatamente o
total.

Também não existe, no backend, suporte para aplicar acréscimo ou desconto a uma comanda com
uma descrição/motivo (ex.: erro de lançamento, cortesia, taxa de serviço). Situações do dia a
dia do balcão que exigem ajuste manual do valor da comanda hoje não têm como ser registradas
nem auditadas. O frontend já tem um fluxo pronto para isso (`useComandasState.ts`), mas
bloqueado à espera do backend — hoje sempre envia acréscimo e desconto como zero.

Ambas as lacunas foram reportadas durante teste real de uso do sistema (issues #40 e #39).

## Objetivo

Um operador de balcão consegue, ao fechar uma comanda ou quitar um fiado:
1. Registrar mais de um pagamento até completar o total devido, com o saldo restante
   corretamente rastreado e, quando aplicável, tratado como fiado.
2. Aplicar um acréscimo ou desconto ao valor da comanda, com uma descrição obrigatória do
   motivo, antes ou no momento do fechamento — e esse ajuste fica registrado para auditoria.

## Fora de escopo

- Alterar o cálculo do total original da comanda a partir dos itens/produtos vendidos.
- Estornar ou cancelar um pagamento já registrado.
- Editar ou remover um acréscimo/desconto depois que a comanda foi fechada/quitada.
- Relatórios ou telas de auditoria dedicadas a acréscimos/descontos (a persistência do motivo
  é requisito desta feature; a exibição em relatório fica para uma feature futura).
- Alterações no frontend além do necessário para desbloquear o fluxo já existente
  (o desbloqueio do placeholder em `useComandasState.ts`/`Comandas.tsx` está dentro do
  escopo; qualquer redesenho de UI não está).
- Dividir um único pagamento entre mais de uma forma de pagamento simultaneamente
  (ex.: metade em PIX e metade em dinheiro no mesmo lançamento) — cada pagamento registrado
  tem uma única forma de pagamento; múltiplos pagamentos com formas diferentes já atendem o
  caso de uso relatado.

## Personas e cenários de uso

- **Operador de balcão**: fecha comandas e quita fiados no dia a dia. Precisa registrar
  pagamentos parciais quando o cliente não paga tudo de uma vez, e precisa aplicar
  acréscimo/desconto quando há erro de lançamento, cortesia ou taxa de serviço.
- **Gestor do bar**: revisa o caixa e as pendências de fiado, e precisa que todo ajuste de
  valor tenha um motivo registrado para poder auditar depois.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | O sistema deve permitir registrar um pagamento de comanda aberta com `valor_pago` menor que o total, mantendo a comanda com um saldo restante rastreável. | obrigatório |
| RF-02 | O sistema deve permitir registrar múltiplos pagamentos para a mesma comanda até que a soma dos valores pagos alcance o total (considerando ajustes de acréscimo/desconto, se houver). | obrigatório |
| RF-03 | O sistema deve rastrear o status da comanda como aberta, parcialmente paga ou quitada/fechada, conforme a soma dos pagamentos registrados em relação ao total. | obrigatório |
| RF-04 | O sistema deve impedir que a soma dos pagamentos de uma comanda ultrapasse o total devido. | obrigatório |
| RF-05 | Ao registrar um pagamento parcial em dinheiro/PIX/cartão que não cobre o total, o sistema deve permitir que o saldo restante seja tratado como fiado (associado a um cliente), preservando o fluxo de fiado já existente para esse saldo. | obrigatório |
| RF-06 | O sistema deve permitir quitar uma pendência de fiado com um valor menor que o saldo devido, mantendo o restante como pendência em aberto. | obrigatório |
| RF-07 | O sistema deve permitir aplicar um acréscimo ou um desconto ao valor de uma comanda antes ou no momento do fechamento, exigindo uma descrição/motivo não vazio para o ajuste. | obrigatório |
| RF-08 | O sistema deve rejeitar a aplicação de acréscimo ou desconto sem descrição/motivo preenchido. | obrigatório |
| RF-09 | O sistema deve persistir o(s) acréscimo(s)/desconto(s) aplicados a uma comanda, incluindo valor, tipo (acréscimo ou desconto) e descrição, de forma consultável posteriormente (auditoria). | obrigatório |
| RF-10 | O valor final devido pela comanda (usado para validar pagamentos e quitação) deve refletir os acréscimos/descontos aplicados. | obrigatório |
| RF-11 | O sistema deve impedir acréscimo/desconto que resulte em valor final da comanda negativo. | obrigatório |
| RF-12 | O sistema deve impedir aplicar acréscimo/desconto a uma comanda que já está fechada ou cancelada. | obrigatório |
| RF-13 | O sistema deve expor, ao consultar uma comanda, o total original, o total ajustado (com acréscimo/desconto) e o saldo restante a pagar (podendo ser negativo, indicando saldo credor). | obrigatório |
| RF-14 | Uma comanda com pelo menos um pagamento já registrado não deve aceitar novos itens/produtos — apenas novos pagamentos ou marcação de saldo como fiado, até o saldo ser zerado. | obrigatório |
| RF-15 | O sistema deve permitir aplicar acréscimo/desconto a uma comanda a qualquer momento até seu fechamento/quitação, mesmo com pagamentos parciais já registrados, recalculando o saldo restante. | obrigatório |
| RF-16 | Quando um acréscimo/desconto aplicado reduzir o total ajustado para um valor menor que a soma já paga, o sistema deve permitir a operação e refletir o resultado como saldo credor (negativo) da comanda, sem processá-lo automaticamente (estorno/troco fica fora do escopo). | obrigatório |

## Requisitos não funcionais

| ID | Requisito | Critério mensurável |
|---|---|---|
| RNF-01 | Consistência: o cálculo de saldo restante e status da comanda deve ser sempre derivado dos pagamentos e ajustes persistidos, nunca de um valor duplicado sujeito a divergência. | 0 inconsistências entre `total ajustado - soma(pagamentos)` e o saldo exposto pela API, verificado pelos testes automatizados da feature. |

## Critérios de aceite

Escritos em DADO / QUANDO / ENTÃO / MAS. Cada critério vira um cenário em
`app/tests/bdd/` sem tradução no meio.

```gherkin
# language: pt
Funcionalidade: Fechamento avançado de comanda

  Cenário: Pagamento parcial de comanda aberta com saldo restante rastreado
    Dado uma comanda aberta com total de 100,00
    Quando um pagamento de 60,00 em dinheiro é registrado para essa comanda
    Então a comanda passa a ter status parcialmente paga
    E o saldo restante da comanda é 40,00
    Mas a comanda não deve ser marcada como fechada

  Cenário: Múltiplos pagamentos até completar o total
    Dado uma comanda aberta com total de 100,00 e um pagamento anterior de 60,00 já registrado
    Quando um segundo pagamento de 40,00 em PIX é registrado para essa comanda
    Então a comanda passa a ter status fechada
    E o saldo restante da comanda é 0,00

  Cenário: Pagamento que ultrapassa o saldo restante é rejeitado
    Dado uma comanda aberta com total de 100,00 e um pagamento anterior de 60,00 já registrado
    Quando um pagamento de 50,00 é registrado para essa comanda
    Então o sistema rejeita a operação com erro de valor pago inválido
    Mas nenhum pagamento novo deve ser persistido

  Cenário: Saldo restante de pagamento parcial vira fiado
    Dado uma comanda aberta com total de 100,00 e um pagamento anterior de 60,00 já registrado
    Quando o saldo restante dessa comanda é marcado como fiado para um cliente cadastrado
    Então a comanda passa a ter status pendente
    E o valor devido em aberto no módulo de fiado é 40,00

  Cenário: Quitação parcial de pendência de fiado
    Dado uma comanda pendente de fiado com saldo devido de 40,00
    Quando um pagamento de quitação de 25,00 é registrado para essa pendência
    Então a comanda permanece com status pendente
    E o saldo devido da pendência passa a ser 15,00

  Cenário: Quitação total de pendência de fiado encerra a pendência
    Dado uma comanda pendente de fiado com saldo devido de 15,00
    Quando um pagamento de quitação de 15,00 é registrado para essa pendência
    Então a comanda passa a ter status fechada
    E a pendência não aparece mais na listagem de pendências em aberto

  Cenário: Aplicar desconto com descrição ao fechamento
    Dado uma comanda aberta com total original de 100,00
    Quando um desconto de 10,00 com descrição "cortesia" é aplicado a essa comanda
    Então o total ajustado da comanda passa a ser 90,00
    E o desconto aplicado fica registrado com a descrição "cortesia"

  Cenário: Aplicar acréscimo com descrição ao fechamento
    Dado uma comanda aberta com total original de 100,00
    Quando um acréscimo de 5,00 com descrição "taxa de serviço" é aplicado a essa comanda
    Então o total ajustado da comanda passa a ser 105,00
    E o acréscimo aplicado fica registrado com a descrição "taxa de serviço"

  Cenário: Acréscimo ou desconto sem descrição é rejeitado
    Dado uma comanda aberta com total original de 100,00
    Quando um desconto de 10,00 é aplicado a essa comanda sem descrição
    Então o sistema rejeita a operação com erro de descrição obrigatória
    Mas o total da comanda não deve ser alterado

  Cenário: Desconto maior que o total é rejeitado
    Dado uma comanda aberta com total original de 100,00
    Quando um desconto de 150,00 com descrição "erro de lançamento" é aplicado a essa comanda
    Então o sistema rejeita a operação com erro de valor de ajuste inválido
    Mas o total da comanda não deve ser alterado

  Cenário: Acréscimo/desconto não pode ser aplicado a comanda já fechada
    Dado uma comanda fechada
    Quando um desconto de 10,00 com descrição "erro de lançamento" é aplicado a essa comanda
    Então o sistema rejeita a operação com erro de comanda não está aberta
    Mas o total da comanda não deve ser alterado

  Cenário: Pagamento respeita total ajustado por desconto
    Dado uma comanda aberta com total original de 100,00 e um desconto de 10,00 com descrição "cortesia" já aplicado
    Quando um pagamento de 90,00 é registrado para essa comanda
    Então a comanda passa a ter status fechada
    Mas um pagamento de 100,00 para essa mesma comanda deve ser rejeitado por ultrapassar o saldo restante

  Cenário: Comanda com pagamento parcial não aceita novos itens
    Dado uma comanda aberta com total de 100,00 e um pagamento anterior de 60,00 já registrado
    Quando um novo item é adicionado a essa comanda
    Então o sistema rejeita a operação com erro de comanda não aceita novos itens
    Mas o total da comanda não deve ser alterado

  Cenário: Múltiplos acréscimos/descontos se acumulam no total ajustado
    Dado uma comanda aberta com total original de 100,00
    Quando um desconto de 10,00 com descrição "cortesia" é aplicado a essa comanda
    E um acréscimo de 5,00 com descrição "taxa de serviço" é aplicado a essa comanda
    Então o total ajustado da comanda passa a ser 95,00
    E os dois ajustes ficam registrados individualmente com suas descrições

  Cenário: Desconto após pagamento parcial recalcula o saldo restante
    Dado uma comanda aberta com total original de 100,00 e um pagamento anterior de 60,00 já registrado
    Quando um desconto de 20,00 com descrição "erro de lançamento" é aplicado a essa comanda
    Então o total ajustado da comanda passa a ser 80,00
    E o saldo restante da comanda passa a ser 20,00

  Cenário: Desconto após pagamento gera saldo credor
    Dado uma comanda aberta com total original de 100,00 e um pagamento anterior de 60,00 já registrado
    Quando um desconto de 50,00 com descrição "erro de lançamento" é aplicado a essa comanda
    Então o total ajustado da comanda passa a ser 50,00
    E o saldo restante da comanda passa a ser -10,00, indicando saldo credor
```

## Esclarecimentos

| Pergunta | Resposta | Data |
|---|---|---|
| Quando o saldo restante de um pagamento parcial não é marcado como fiado, a comanda fica bloqueada para novos itens até ser quitada ou virar fiado? | Sim. Uma vez que há pelo menos um pagamento registrado contra a comanda, ela não aceita mais itens novos — só pagamentos ou marcação como fiado até o saldo zerar. | 2026-09-20 |
| Acréscimo/desconto pode ser percentual, além de valor fixo? | Não nesta feature. Apenas valor fixo em R$. Percentual fica para feature futura. | 2026-09-20 |
| Pode haver mais de um acréscimo/desconto na mesma comanda? | Sim. Cada aplicação é um lançamento auditável próprio; o total ajustado é o total original mais a soma de todos os ajustes (acréscimos somam, descontos subtraem). | 2026-09-20 |
| Acréscimo/desconto pode ser aplicado com pagamento parcial já registrado? | Sim, a qualquer momento até o fechamento/quitação da comanda, recalculando o saldo restante. | 2026-09-20 |
| Se um desconto aplicado depois de pagamentos parciais reduzir o total ajustado para menos do que já foi pago, o que acontece? | O ajuste é permitido mesmo assim, e a comanda passa a ter saldo credor (valor negativo) em favor do cliente. O tratamento desse saldo credor (troco, abatimento em consumo futuro, estorno) fica fora do escopo desta feature — apenas o registro e a exposição do saldo credor fazem parte dela. | 2026-09-20 |

## Métricas de sucesso

- Comandas com pagamento parcial (mais de um pagamento associado) passam a existir e ser
  fechadas corretamente em produção, sem chamados de suporte relatando "não consigo dividir o
  pagamento".
- Zero lançamentos manuais fora do sistema (planilha paralela, anotação em papel) para
  registrar acréscimo/desconto, verificado por relato do usuário após adoção.

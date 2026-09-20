# Especificação — Fiado avulso retroativo

> Descreve **o quê** e **por quê**. Não descreve como implementar: sem nome de biblioteca,
> sem esquema de banco, sem assinatura de função.

## Problema

Hoje só é possível gerar um fiado a partir de uma comanda que acabou de ser fechada dentro
do próprio sistema. Bares que já têm fiado em andamento com clientes antes de começar a usar
o sistema (ex.: uma "caderneta" de fiado em papel) não têm como migrar esse histórico: não
existe um fluxo para registrar, diretamente no cadastro do cliente, uma dívida que já existia
antes, com sua data de origem real (no passado). Sem isso, o bar precisa "zerar" o controle ao
migrar ou manter dois controles em paralelo (papel + sistema), o que já foi relatado como
problema em teste real de uso.

## Objetivo

Um usuário do sistema consegue lançar, para um cliente cadastrado, uma pendência de fiado
avulsa — sem depender de uma comanda aberta e fechada agora no sistema — informando o valor
devido e a data em que a dívida realmente começou, incluindo datas passadas anteriores ao uso
do sistema. Essa pendência passa a existir nas mesmas listagens, consultas e no mesmo fluxo de
quitação que hoje atendem o fiado originado de comanda, sem exigir um fluxo paralelo para o
cliente ou para os relatórios do bar.

## Fora de escopo

- Pagamento parcial da pendência avulsa.
- Juros ou correção sobre a dívida migrada.
- Parcelamento da dívida migrada.
- Limite de crédito por cliente.
- Cobrança automática ou notificação ao cliente.
- Edição ou exclusão de uma pendência avulsa já lançada.
- Importação em lote (múltiplas dívidas de uma vez); o lançamento é um a um.
- Vincular a pendência avulsa a itens de produto/consumo (ela representa apenas um valor devido).

## Personas e cenários de uso

- **Operador do bar migrando histórico**: ao adotar o sistema, percorre a caderneta de papel
  e, para cada cliente com dívida em aberto, lança uma pendência avulsa com o valor e a data em
  que o cliente começou a dever — muitas vezes dias, semanas ou meses atrás.
- **Operador do bar no dia a dia**: depois de migrado o histórico, consulta a lista de
  pendências do cliente (as vindas de comanda e as avulsas juntas) para saber quanto ele deve
  no total, e quita a dívida da mesma forma que quita qualquer fiado hoje.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-01 | O sistema deve permitir lançar uma pendência de fiado avulsa vinculada a um cliente cadastrado, sem exigir uma comanda aberta ou fechada no sistema. | obrigatório |
| RF-02 | O sistema deve exigir, no lançamento avulso, o cliente, o valor devido e a data de origem da dívida. | obrigatório |
| RF-03 | O sistema deve aceitar, na data de origem da dívida, qualquer data igual ou anterior à data atual. | obrigatório |
| RF-04 | O sistema deve rejeitar data de origem no futuro. | obrigatório |
| RF-05 | O sistema deve rejeitar valor devido igual ou menor que zero. | obrigatório |
| RF-06 | O sistema deve exigir que o cliente do lançamento avulso esteja cadastrado e ativo, da mesma forma que hoje é exigido para o fiado originado de comanda. | obrigatório |
| RF-07 | A pendência avulsa deve aparecer nas mesmas listagens e consultas de pendências (todas, por cliente, vencidas) que já existem para o fiado hoje. | obrigatório |
| RF-08 | A pendência avulsa deve poder ser quitada pelo mesmo fluxo de quitação que já existe para o fiado hoje, com o mesmo efeito sobre o caixa. | obrigatório |
| RF-09 | A pendência avulsa deve permitir registrar uma observação opcional, da mesma forma que o fiado originado de comanda permite hoje. | desejável |
| RF-10 | A pendência avulsa deve ter um vencimento, seguindo a mesma regra já aplicada ao fiado originado de comanda: vencimento futuro informado manualmente, ou padrão do sistema (hoje + dias configurados) quando não informado. | obrigatório |
| RF-11 | O lançamento da pendência avulsa não deve exigir caixa aberto no momento do lançamento, por não movimentar dinheiro nem caixa. | obrigatório |

## Requisitos não funcionais

Nenhum requisito não funcional novo além dos já cobertos pela constituição do projeto
(cobertura mínima de 90% por arquivo modificado).

## Critérios de aceite

```gherkin
# language: pt
Funcionalidade: Fiado avulso retroativo

  Cenário: Lançar pendência avulsa com data de origem no passado
    Dado um cliente cadastrado e ativo, sem nenhuma comanda pendente hoje
    Quando o operador lança uma pendência de fiado avulsa para esse cliente, com valor devido e data de origem de um mês atrás
    Então a pendência passa a existir para o cliente, com o valor, a data de origem e o vencimento informados
    Mas nenhuma comanda precisa existir para essa pendência ter sido criada

  Cenário: Lançar pendência avulsa sem caixa aberto
    Dado um cliente cadastrado e ativo e nenhum caixa aberto no momento
    Quando o operador lança uma pendência de fiado avulsa para esse cliente
    Então a pendência é criada normalmente
    Mas nenhuma exigência de caixa aberto bloqueia o lançamento

  Cenário: Rejeitar data de origem no futuro
    Dado um cliente cadastrado e ativo
    Quando o operador tenta lançar uma pendência de fiado avulsa com data de origem no futuro
    Então o sistema rejeita o lançamento
    Mas nenhuma pendência é criada

  Cenário: Rejeitar valor devido inválido
    Dado um cliente cadastrado e ativo
    Quando o operador tenta lançar uma pendência de fiado avulsa com valor devido igual a zero
    Então o sistema rejeita o lançamento
    Mas nenhuma pendência é criada

  Cenário: Exigir cliente ativo para pendência avulsa
    Dado um cliente cadastrado e inativo
    Quando o operador tenta lançar uma pendência de fiado avulsa para esse cliente
    Então o sistema rejeita o lançamento
    Mas nenhuma pendência é criada

  Cenário: Pendência avulsa aparece na listagem de pendências do cliente
    Dado um cliente com uma pendência de fiado avulsa já lançada
    Quando o operador consulta as pendências desse cliente
    Então a pendência avulsa aparece na lista, junto de qualquer outra pendência originada de comanda
    Mas a listagem não distingue de forma que quebre o fluxo já existente de consulta

  Cenário: Quitar pendência avulsa pelo fluxo já existente
    Dado um cliente com uma pendência de fiado avulsa em aberto e um caixa aberto no dia
    Quando o operador quita essa pendência pelo mesmo fluxo de quitação do fiado
    Então a pendência deixa de aparecer como pendente
    E o valor pago é registrado no caixa aberto, da mesma forma que hoje ocorre para o fiado originado de comanda
```

## Esclarecimentos

| Pergunta | Resposta | Data |
|---|---|---|
| A pendência avulsa precisa de vencimento, como o fiado de comanda tem hoje? | Sim, segue a mesma regra atual: vencimento futuro informado manualmente, ou padrão do sistema quando não informado. | 2026-09-19 |
| Lançar a pendência avulsa exige caixa aberto no momento? | Não exige — é só registro histórico, não movimenta caixa nem dinheiro. | 2026-09-19 |
| Existe limite de quão antiga pode ser a data de origem? | Sem limite — qualquer data passada é aceita; a única regra é não poder ser no futuro. | 2026-09-19 |

## Ambiguidades

Nenhuma pendente — ver tabela `Esclarecimentos` ao final.

## Métricas de sucesso

- Um bar em processo de adoção do sistema consegue migrar 100% do saldo devedor de fiado que
  tinha em controle paralelo (papel) para o sistema, sem precisar "zerar" o controle anterior.
- Depois da migração, a lista de pendências e o total a receber do cliente refletem, em um só
  lugar, tanto as dívidas migradas quanto as novas geradas por comanda.

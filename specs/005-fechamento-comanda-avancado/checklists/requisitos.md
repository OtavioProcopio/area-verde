# Checklist — Fechamento avançado de comanda: pagamento parcial e acréscimo/desconto / Requisitos

> Avalia a **qualidade da especificação**, não do código. `[x]` significa "requisito
> aprovado por revisor humano". O agente não se autoaprova.

## Completude

- [ ] Todo requisito funcional (RF-01 a RF-16) tem ao menos um critério de aceite em DADO/QUANDO/ENTÃO correspondente
- [ ] O único requisito não funcional (RNF-01) tem critério mensurável, com número e unidade
- [ ] A seção "Fora de escopo" cobre estorno de pagamento, edição de ajuste após fechamento, relatório de auditoria e divisão de um único pagamento entre formas
- [ ] A tabela "Esclarecimentos" registra as 5 decisões tomadas (bloqueio de itens, valor fixo vs. percentual, múltiplos ajustes, ajuste a qualquer momento, saldo credor)

## Clareza

- [ ] Nenhuma marca `[NECESSITA ESCLARECIMENTO]` restante no `spec.md`
- [ ] A definição de "saldo credor" (RF-16) e sua origem (desconto aplicado após pagamento parcial) não admite duas leituras
- [ ] A diferença entre "comanda parcialmente paga" (RF-03) e "comanda pendente de fiado" fica clara — não são o mesmo status
- [ ] O critério de aceite "Comanda com pagamento parcial não aceita novos itens" descreve comportamento observável, não implementação

## Consistência

- [ ] RF-04 (soma dos pagamentos não pode ultrapassar o total) não contradiz RF-16 (saldo credor pode ser negativo por causa de desconto posterior, não por excesso de pagamento)
- [ ] RF-15 (ajuste a qualquer momento até o fechamento) é compatível com RF-12 (ajuste proibido em comanda fechada/cancelada) sem sobreposição ambígua sobre comanda pendente de fiado
- [ ] Vocabulário é consistente: "total original", "total ajustado" e "saldo restante" são usados sempre com o mesmo significado em toda a spec
- [ ] Nenhum requisito desta spec contradiz o comportamento já existente de fiado avulso retroativo (`specs/001-fiado-avulso-retroativo`)

## Testabilidade

- [ ] Todo critério de aceite Gherkin usa valores numéricos concretos (não "um valor qualquer"), permitindo assert direto sem reinterpretação
- [ ] Existe cenário de erro para: pagamento que ultrapassa saldo, ajuste sem descrição, desconto maior que o total, ajuste em comanda fechada, item novo em comanda parcialmente paga
- [ ] O cenário de saldo credor (RF-16) tem valores que permitem verificar o sinal negativo do saldo, não só sua existência

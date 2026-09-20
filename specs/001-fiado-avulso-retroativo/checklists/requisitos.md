# Checklist — Fiado avulso retroativo / Requisitos

> Avalia a **qualidade da especificação**, não do código. `[x]` significa "requisito
> aprovado por revisor humano". O agente não se autoaprova.

## Completude

- [ ] Todo requisito funcional (RF-01 a RF-11) tem ao menos um critério de aceite em DADO/QUANDO/ENTÃO
- [ ] O que está fora de escopo está escrito e cobre os casos que alguém razoavelmente esperaria (edição, exclusão, pagamento parcial, juros, importação em lote)
- [ ] A seção de Objetivo descreve um resultado observável, não uma tarefa técnica

## Clareza

- [ ] Nenhuma marca `[NECESSITA ESCLARECIMENTO]` restante
- [ ] Nenhum requisito admite duas leituras conflitantes (ex.: "data de origem" não é confundida com "data do lançamento no sistema")
- [ ] Nenhum requisito descreve implementação em vez de comportamento

## Consistência

- [ ] Nenhum requisito contradiz outro (ex.: RF-01 dispensar comanda não contradiz RF-08 exigir o mesmo fluxo de quitação)
- [ ] Nenhum requisito contradiz a constituição do projeto
- [ ] Vocabulário do domínio (cliente, pendência, vencimento, quitação, caixa) é o mesmo em todo o documento e o mesmo já usado em `docs/modules/fiado.md`

## Testabilidade

- [ ] Todo critério de aceite pode virar cenário executável sem reinterpretação
- [ ] Todo caminho de erro relevante (data no futuro, valor inválido, cliente inativo) tem cenário próprio
- [ ] O critério de quitação cobre o efeito observável sobre o caixa, não só a mudança de status

# Checklist — Validar nome duplicado no cadastro de produto / Requisitos

> Avalia a **qualidade da especificação**, não do código. `[x]` significa "requisito
> aprovado por revisor humano". O agente não se autoaprova.

## Completude

- [ ] Todo requisito funcional (RF-01 a RF-07) tem ao menos um critério de aceite em DADO/QUANDO/ENTÃO
- [ ] Fora de escopo cobre o que alguém razoavelmente esperaria (correção de duplicados já existentes, sugestão automática de nome)
- [ ] O objetivo descreve um resultado observável, não uma tarefa técnica

## Clareza

- [ ] Nenhuma marca `[NECESSITA ESCLARECIMENTO]` restante
- [ ] Nenhum requisito admite duas leituras conflitantes (ex.: escopo global vs. por categoria já está resolvido e documentado)
- [ ] Nenhum requisito descreve implementação em vez de comportamento

## Consistência

- [ ] Nenhum requisito contradiz outro
- [ ] Nenhum requisito contradiz a constituição do projeto
- [ ] Vocabulário do domínio (produto, categoria, ativo/inativo) é o mesmo já usado em `docs/modules/produtos-categorias.md`

## Testabilidade

- [ ] Todo critério de aceite pode virar cenário executável sem reinterpretação
- [ ] O caminho de erro (nome duplicado) tem cenário próprio para criação, edição e produto composto
- [ ] O caso de reaproveitar nome de produto inativo tem cenário próprio

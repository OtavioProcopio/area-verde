# Checklist — Reorganizar testes do backend / Requisitos

> Avalia a **qualidade da especificação**, não do código. `[x]` significa "requisito
> aprovado por revisor humano". O agente não se autoaprova.

## Completude

- [ ] Todo requisito funcional (RF-01 a RF-05) tem ao menos um critério de aceite em DADO/QUANDO/ENTÃO
- [ ] Fora de escopo deixa explícito que não é reescrita de teste, só reorganização de arquivo
- [ ] O objetivo descreve um resultado observável (área de testes organizada, nada quebrado)

## Clareza

- [ ] Nenhuma marca `[NECESSITA ESCLARECIMENTO]` restante
- [ ] A granularidade do espelhamento por camada está definida sem ambiguidade (Esclarecimentos)
- [ ] Nenhum requisito descreve implementação em vez de comportamento esperado

## Consistência

- [ ] Nenhum requisito contradiz outro
- [ ] Nenhum requisito contradiz a constituição do projeto
- [ ] O vocabulário (camada, módulo, área de testes) é usado de forma consistente no documento

## Testabilidade

- [ ] "Nenhum teste perdido" (RF-03) é verificável objetivamente (contagem de testes antes/depois)
- [ ] "Automação continua funcionando" (RF-04) é verificável rodando `make validate`
- [ ] "Documentação atualizada" (RF-05) é verificável buscando referências de caminho antigo

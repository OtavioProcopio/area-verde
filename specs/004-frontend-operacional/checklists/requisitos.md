# Checklist — Corrigir documentação que trata o frontend como pendente/futuro / requisitos

> Avalia a **qualidade da especificação**, não do código. `[x]` significa "requisito
> aprovado por revisor humano". O agente não se autoaprova.

## Completude

- [ ] Todo requisito funcional (RF-01 a RF-04) tem ao menos um critério de aceite em DADO/QUANDO/ENTÃO
- [ ] O que está fora de escopo está escrito (código, auditoria completa de docs, docker-compose.local.yml, detalhe do frontend)

## Clareza

- [ ] Nenhuma marca `[NECESSITA ESCLARECIMENTO]` restante
- [ ] Nenhum requisito admite duas leituras conflitantes
- [ ] Nenhum requisito descreve implementação em vez de comportamento

## Consistência

- [ ] Nenhum requisito contradiz outro
- [ ] Nenhum requisito contradiz a constituição
- [ ] Vocabulário do domínio é o mesmo em todo o documento (frontend, área-verde-frontend, pendente/implementado)

## Testabilidade

- [ ] Todo critério de aceite pode ser verificado lendo o arquivo final (grep ou leitura direta)
- [ ] O critério de consistência entre os 3 arquivos (RF-04) tem cenário próprio

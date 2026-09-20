# Plano de implementação — Corrigir documentação que trata o frontend como pendente/futuro

> Descreve **como**. Deriva da spec e da constituição; não introduz requisito novo.

## Decisões técnicas

| Decisão | Escolha | Alternativas descartadas | Por quê |
|---|---|---|---|
| Onde registrar que o frontend existe | Editar os 3 arquivos já identificados na spec (`README.md`, `docs/roadmap.md`, `docs/matrix/pending-gaps.md`), sem criar arquivo novo | Criar uma seção "Integrações" nova em `docs/` | A spec já delimita o escopo aos 3 arquivos que fazem a afirmação incorreta — criar estrutura nova seria requisito não pedido |
| Como classificar o frontend no roadmap | Nova seção "Integrado" (mesmo nível de "Implementado"/"Próximo"/"Depois"), já que o frontend não é um módulo do backend, é outro repositório consumindo a API | Colocar dentro de "Implementado" (que hoje só lista módulos do backend) | Evita confundir "módulo do backend implementado" com "sistema externo em uso" — mais preciso |
| Como registrar a correção em `pending-gaps.md` | Reescrever a linha existente na tabela + acrescentar entrada na seção "Itens corrigidos neste PR documental" (padrão já usado no arquivo) | Só apagar a linha, sem registrar a correção | O próprio arquivo já tem essa seção como histórico de correções — manter o padrão |

## Padrões de projeto aplicados

Nenhum — feature documental, sem código.

## Arquivos a criar ou alterar

| Camada | Arquivo | Ação | Teste espelhado |
|---|---|---|---|
| docs | `README.md` | alterar (mover linha "Frontend" da tabela "Pendente" para uma nova linha/seção "Integrado") | — (documentação não tem teste automatizado; verificação é o `grep` do RF-04/Métricas de sucesso) |
| docs | `docs/roadmap.md` | alterar (mover "Frontend operacional" de "Depois"/item 13 "Futuro" para uma seção "Integrado") | — |
| docs | `docs/matrix/pending-gaps.md` | alterar (reescrever a linha "Frontend operacional — Futuro" e registrar em "Itens corrigidos") | — |

Nenhum arquivo de código (`app/`) é tocado.

## Contrato entre camadas

Não aplicável — feature documental.

## Dependências externas

Nenhuma.

## Impacto no contrato de operação

Nenhum alvo de Makefile novo. Nenhuma alteração de código, então `make validate` não muda de
comportamento — a verificação desta feature é leitura (grep + revisão manual), não teste
automatizado.

## Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Reescrever demais e alterar informação que não é sobre o frontend | Baixa | Tocar só as linhas/seções que mencionam frontend nos 3 arquivos, nada mais |
| Ordem consolidada do roadmap ficar com numeração quebrada após mover o item 13 | Baixa | Renumerar a tabela completa ao mover, não só remover a linha |

## Conformidade com a constituição

| Princípio | Como este plano o respeita |
|---|---|
| Contrato de operação | Nenhum alvo de Makefile necessário — feature é edição de Markdown, não código executável. |
| Arquitetura limpa | Não aplicável — nenhum arquivo em `app/` é tocado. |
| Testes provam a entrega | Não aplicável a documentação; a verificação é o `grep` e a revisão de consistência entre os 3 arquivos, declarados na spec como Métricas de sucesso. |
| Simplicidade defensável | Menor mudança possível: reclassifica 3 linhas/seções existentes, não reescreve os arquivos inteiros nem introduz estrutura nova. |

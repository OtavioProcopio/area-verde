# Tarefas — Corrigir documentação que trata o frontend como pendente/futuro

> Ordem de dependência. `[P]` marca tarefa paralelizável (não toca arquivo de outra `[P]`
> da mesma fase). Feature documental — não há BDD/teste automatizado aplicável; a
> verificação é leitura (grep + revisão manual), declarada no próprio critério de aceite.

## Fase 1 — Correção dos 3 arquivos

> Cada tarefa toca um arquivo diferente das outras — `[P]`.

- [x] T001 [P] Alterar `README.md` — mover a linha "Frontend" da tabela "Pendente" (seção Funcionalidades) para uma nova linha em seção "Integrado", com link para `area-verde-frontend` (RF-01)
- [x] T002 [P] Alterar `docs/roadmap.md` — mover "Frontend operacional" de "Depois"/"Futuro" e da "Ordem consolidada" (item 13) para uma nova seção "Integrado", renumerando a ordem consolidada (RF-02)
- [x] T003 [P] Alterar `docs/matrix/pending-gaps.md` — reescrever a linha "Frontend operacional — Futuro — Ainda não há aplicação visual" e registrar a correção na seção "Itens corrigidos neste PR documental" (RF-03)

## Fase 2 — Verificação final

- [x] T004 Rodar `grep -rn "Futuro\|Pendente\|Depois" README.md docs/roadmap.md docs/matrix/pending-gaps.md` e confirmar que nenhuma ocorrência associa essas palavras ao frontend (RF-04)
- [x] T005 Revisão manual: ler os 3 arquivos e confirmar que nenhum contradiz outro sobre o status do frontend

## Rastreabilidade

| Requisito | Tarefas |
|---|---|
| RF-01 | T001 |
| RF-02 | T002 |
| RF-03 | T003 |
| RF-04 | T004, T005 |

## Convergence

> Seção **append-only**, escrita por `/bu:converge`. Cada rodada acrescenta um bloco;
> nada é reescrito.

### Rodada 1 — 2026-09-20

| Requisito | Estado | Evidência |
|---|---|---|
| RF-01 | realizado | `README.md` — seção "Integrado" nova, linha "Frontend" fora da tabela "Pendente" |
| RF-02 | realizado | `docs/roadmap.md` — seção "Integrado" nova, item 13 da ordem consolidada com status "Integrado (repositório próprio)" |
| RF-03 | realizado | `docs/matrix/pending-gaps.md` — linha "Frontend operacional — Futuro" removida da tabela de média/baixa prioridade, entrada nova na seção "Itens corrigidos neste PR documental" |
| RF-04 | realizado | `grep -in "futuro\|pendente\|depois" README.md docs/roadmap.md docs/matrix/pending-gaps.md \| grep -i frontend` só retorna a linha do próprio changelog "Itens corrigidos" (descrevendo a situação *anterior*, não uma afirmação atual); leitura manual dos 3 arquivos não encontrou contradição |

Sem `make validate` nesta rodada — feature 100% documental, nenhum arquivo em `app/` foi
tocado (declarado desde o plano).

**Excesso**: `docs/roadmap.md` também tinha "Frontend" na lista "Fora do escopo imediato"
(fora do que a spec citava explicitamente) — corrigido junto por ser a mesma inconsistência
no mesmo arquivo que RF-02 já cobria; não é escopo novo, é a mesma correção aplicada a mais
uma linha do mesmo arquivo.

Nenhum item da seção **Fora de escopo** da spec foi violado: nenhum código tocado, nenhum
outro arquivo de `docs/` alterado além dos 3 citados.

Veredito: **convergido**
Tarefas acrescentadas: nenhuma

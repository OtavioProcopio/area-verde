# Tarefas — Reorganizar testes do backend para espelhar a arquitetura em camadas

> Ordem de dependência. `[P]` marca tarefa paralelizável (não toca arquivo de outra `[P]`
> da mesma fase). Esta feature não introduz comportamento novo — a "prova" de cada tarefa é a
> suíte inteira continuar passando com a mesma contagem de testes e cobertura, verificada logo
> após cada lote de movimentação (substitui "teste antes da implementação", que não se aplica a
> um `git mv` puro).

## Fase 1 — Linha de base

- [x] T001 Rodar `make validate` (com `RUN_MIGRATIONS=false`) antes de qualquer `git mv` e registrar: quantidade de testes coletados, cobertura total, cobertura por arquivo dos 12 arquivos de teste atuais — linha de base para comparar depois de cada lote

## Fase 2 — Mover os testes de módulo de negócio

Nenhuma tarefa é `[P]`: todas tocam o mesmo diretório novo (`app/tests/core/application/use_cases/`) e a criação do diretório só precisa acontecer uma vez.

- [x] T002 Criar `app/tests/core/application/use_cases/` e mover (`git mv`) os 10 arquivos de teste de módulo de negócio: `caixa_test.py`, `clientes_test.py`, `comandas_test.py`, `configuracoes_test.py`, `estoque_test.py`, `fiado_test.py`, `pagamentos_test.py`, `produto_composicao_test.py`, `produtos_categorias_test.py`, `relatorios_test.py` (RF-01, RF-02)
- [x] T003 Rodar `make test` (com `RUN_MIGRATIONS=false`) e conferir que a quantidade de testes coletados é igual à linha de base de T001 (RF-03)

## Fase 3 — Mover os testes de composição raiz

- [x] T004 Criar `app/tests/` (se ainda não existir) e mover (`git mv`) `bootstrap_test.py` e `health_test.py` para `app/tests/` (raiz da área de testes, não dentro de uma pasta de camada) (RF-01, RF-02)
- [x] T005 Rodar `make validate` (com `RUN_MIGRATIONS=false`) completo e conferir: mesma quantidade de testes da linha de base, cobertura total igual ou maior, nenhum arquivo de teste aparecendo no relatório de cobertura (RF-03, RF-04)

## Fase 4 — Documentação e validação final

- [x] T006 Atualizar `docs/architecture/tests.md` — seção "Padrão de arquivos" e a tabela "Cobertura por módulo" com os caminhos novos
- [x] T007 Atualizar `docs/matrix/tests-by-module.md` com os caminhos novos
- [x] T008 Buscar `_test.py` em todo `docs/`, `README.md` e `CONTRIBUTING.md` e atualizar cada referência de caminho restante (inclui as seções "Testes relacionados" de `docs/modules/*.md`) (RF-05)
- [x] T009 `make validate` verde, com a mesma cobertura total (ou maior) da linha de base de T001

## Rastreabilidade

| Requisito | Tarefas |
|---|---|
| RF-01 | T002, T004 |
| RF-02 | T002, T004 |
| RF-03 | T003, T005, T009 |
| RF-04 | T005, T009 |
| RF-05 | T006, T007, T008 |

## Convergence

> Seção **append-only**, escrita por `/bu:converge`. Cada rodada acrescenta um bloco;
> nada é reescrito.

### Rodada 1 — 2026-09-19

| Requisito | Estado | Evidência |
|---|---|---|
| RF-01 (testes fora da raiz de `app/`) | realizado | `git mv` dos 12 arquivos para `app/tests/` e `app/tests/core/application/use_cases/` |
| RF-02 (granularidade do espelhamento, decidida em clarify) | realizado | 10 testes de módulo em `app/tests/core/application/use_cases/`; `bootstrap_test.py` e `health_test.py` na raiz de `app/tests/` |
| RF-03 (nenhum teste perdido/enfraquecido) | realizado | Linha de base T001: 139 testes, 96,21% cobertura. Após mover (T003, T005, T009): 139 testes, 96,21% cobertura — idêntico, nenhuma asserção tocada |
| RF-04 (automação continua igual) | realizado | `make validate` com o mesmo comando de sempre, sem alteração de `Makefile`, `pytest.ini` ou `.coveragerc` (confirmado empiricamente que `*_test.py` em `omit` casa com caminho aninhado) |
| RF-05 (documentação atualizada) | realizado | `docs/architecture/tests.md`, `docs/matrix/tests-by-module.md`, `docs/matrix/functional-coverage.md` e as seções "Testes relacionados" de 9 `docs/modules/*.md` — busca final por `_test.py` sem nenhuma referência ao caminho antigo |

**Fora de escopo respeitado**: nenhum teste foi reescrito em estilo diferente; nenhum teste novo
foi adicionado; nenhuma divisão por camada (adapter/controllers, adapter/repositories) além do
que RF-02 pediu; `Makefile`/`docker-compose.yml`/CI não foram tocados.

**Excesso de escopo**: nenhum. Só `git mv` de teste e atualização de documentação de caminho.

**`make validate`** (`RUN_MIGRATIONS=false`): `139 passed, 3 warnings` — cobertura total
**96.21%** (idêntica à linha de base antes da reorganização).

Veredito: convergido
Tarefas acrescentadas: nenhuma

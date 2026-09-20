# Plano de implementação — Reorganizar testes do backend para espelhar a arquitetura em camadas

> Descreve **como**. Deriva da spec e da constituição; não introduz requisito novo.

## Decisões técnicas

| Decisão | Escolha | Alternativas descartadas | Por quê |
|---|---|---|---|
| Árvore de destino | `app/tests/core/application/use_cases/<mesmo nome>.py` para os 10 testes de módulo de negócio; `app/tests/bootstrap_test.py` e `app/tests/health_test.py` na raiz da área de testes | Espelhar também `adapter/controllers`, `adapter/repositories` etc. | Decidido em `/bu:clarify` (RF-02): os testes atuais exercitam o fluxo inteiro via API, não uma camada isolada; um teste por arquivo é a única camada que cada arquivo de fato testa de forma centrada — `core/application/use_cases`, já que cada teste tem nome e escopo de um `*_service.py` que mora lá |
| Como mover | `git mv` arquivo por arquivo, preservando histórico de cada um | `rm` + criar novo | `git mv` mantém `git blame`/histórico rastreável; recriar do zero perderia isso sem necessidade |
| `conftest.py` | Continua em `app/conftest.py`, sem mover | Mover para `app/tests/conftest.py` | Pytest descobre `conftest.py` subindo pelos diretórios ancestrais do arquivo de teste; `app/` já é ancestral de `app/tests/**`, então o fixture continua visível sem mudança. Mover não muda comportamento e só adiciona risco (`conftest.py` também está na lista `EXEMPT_NAMES` do hook de estrutura, confirmando que não precisa migrar) |
| `pytest.ini` (`testpaths`, `python_files`) | Sem alteração | Restringir `testpaths` para `app/tests` | `testpaths = .` já descobre `*_test.py` em qualquer subpasta de `app/` (inclusive a nova `app/tests/**`); pytest já ignora `.venv/` por padrão (`norecursedirs`). Restringir não muda o resultado e é mudança desnecessária |
| `.coveragerc` (`omit`) | Sem alteração | Trocar `*_test.py` por um padrão com `**` | Verificado empiricamente (`coverage.files.GlobMatcher`) que o padrão `*_test.py` já casa com caminhos aninhados como `app/tests/core/application/use_cases/fiado_test.py` — a omissão de cobertura continua funcionando sem mudança |
| Makefile / CI | Sem alteração | Adicionar caminho explícito ao comando `pytest` | Os comandos (`pytest . -v -m "not integration"`) já cobrem a nova árvore por estarem sob `app/`; RF-04 exige que o comando em si não mude |

## Padrões de projeto aplicados

| Padrão | Onde | Problema que resolve | Custo aceito |
|---|---|---|---|
| — | — | — | — |

Nenhum padrão GoF: é reorganização de arquivos, não de código de produção.

## Arquivos a criar ou alterar

| Camada | Arquivo | Ação | Teste espelhado |
|---|---|---|---|
| testes | `app/bootstrap_test.py` → `app/tests/bootstrap_test.py` | mover (`git mv`) | é o próprio teste |
| testes | `app/health_test.py` → `app/tests/health_test.py` | mover (`git mv`) | é o próprio teste |
| testes | `app/caixa_test.py` → `app/tests/core/application/use_cases/caixa_test.py` | mover | é o próprio teste |
| testes | `app/clientes_test.py` → `app/tests/core/application/use_cases/clientes_test.py` | mover | é o próprio teste |
| testes | `app/comandas_test.py` → `app/tests/core/application/use_cases/comandas_test.py` | mover | é o próprio teste |
| testes | `app/configuracoes_test.py` → `app/tests/core/application/use_cases/configuracoes_test.py` | mover | é o próprio teste |
| testes | `app/estoque_test.py` → `app/tests/core/application/use_cases/estoque_test.py` | mover | é o próprio teste |
| testes | `app/fiado_test.py` → `app/tests/core/application/use_cases/fiado_test.py` | mover | é o próprio teste |
| testes | `app/pagamentos_test.py` → `app/tests/core/application/use_cases/pagamentos_test.py` | mover | é o próprio teste |
| testes | `app/produto_composicao_test.py` → `app/tests/core/application/use_cases/produto_composicao_test.py` | mover | é o próprio teste |
| testes | `app/produtos_categorias_test.py` → `app/tests/core/application/use_cases/produtos_categorias_test.py` | mover | é o próprio teste |
| testes | `app/relatorios_test.py` → `app/tests/core/application/use_cases/relatorios_test.py` | mover | é o próprio teste |
| docs | `docs/architecture/tests.md` | alterar — "Padrão de arquivos" e tabela de cobertura por módulo com os caminhos novos | — |
| docs | `docs/matrix/tests-by-module.md` | alterar — caminhos novos | — |
| docs | `docs/modules/*.md` (todos os que citam `_test.py` em "Testes relacionados") | alterar — caminhos novos | — |

Nenhum arquivo de produção (`core/`, `adapter/`, `infra/`) é tocado — só testes e documentação.
Nenhum conteúdo de teste muda: só o caminho do arquivo (import interno continua igual, já que
`pythonpath = .` resolve a partir de `app/` independente de onde o arquivo de teste mora).

## Contrato entre camadas

Não se aplica — não há mudança de comportamento entre camadas de produção. O único "contrato"
que muda é onde o pytest encontra cada arquivo, e isso é resolvido pela descoberta padrão de
`testpaths = .` já existente.

## Dependências externas

| Dependência | Versão | Justificativa | Simulada nos testes por |
|---|---|---|---|
| — | — | Nenhuma | — |

## Impacto no contrato de operação

Nenhum. `make test`, `make test-coverage`, `make validate`, `make check`, `make ci` continuam
com o mesmo comando (`pytest . ...`), sem alteração de alvo do `Makefile`.

## Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| `pytest` não descobrir os testes movidos por algum comportamento de `rootdir`/`testpaths` não previsto | Baixa (já verificado que `testpaths = .` cobre qualquer subpasta) | Rodar `make test` logo após cada lote de `git mv` e comparar a contagem de testes coletados com o número original antes de prosseguir |
| Cobertura deixar de omitir os arquivos de teste movidos, inflando artificialmente `--cov-report` | Baixa (verificado empiricamente que `*_test.py` casa com caminho aninhado) | Rodar `make test-coverage` e conferir que os arquivos de teste não aparecem no relatório de cobertura, igual a antes |
| Esquecer alguma referência de caminho de teste em documentação | Média (12 arquivos, vários documentos) | Buscar `_test.py` em todo `docs/` e `README.md`/`CONTRIBUTING.md` antes de considerar a tarefa de documentação concluída, não só nos arquivos óbvios |

## Conformidade com a constituição

| Princípio | Como este plano o respeita |
|---|---|
| Contrato de operação | Nenhum alvo de `Makefile` novo ou alterado; comandos continuam idênticos (RF-04) |
| Arquitetura limpa | Não toca código de produção; a nova área de testes passa a refletir a camada `core/application/use_cases`, que é exatamente o que RF-02 pediu |
| Testes provam a entrega | Nenhuma asserção é removida ou enfraquecida (RF-03); a "prova" desta feature é a suíte inteira continuar passando com a mesma cobertura, verificada via `make validate` ao final de cada lote de movimentação |
| Simplicidade defensável | Reorganização mínima que atende ao pedido — sem reescrever testes em estilo diferente (explicitamente fora de escopo), sem introduzir divisão por camada que exigiria mocks que este projeto não usa nesses testes |
| Autoria | Nenhum artefato atribui autoria a ferramenta de IA |
| Idioma | `spec.md`, este `plan.md` e a documentação atualizada em português |
| Migrations Alembic (específico do projeto) | Não se aplica — nenhuma mudança de schema |

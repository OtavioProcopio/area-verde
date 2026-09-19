# Tarefas — Validar nome duplicado no cadastro de produto

> Ordem de dependência. `[P]` marca tarefa paralelizável (não toca arquivo de outra `[P]`
> da mesma fase). Teste vem antes da implementação que ele prova.

## Fase 1 — Domínio

- [x] T001 Estender `test_product_category_indexes_can_be_created` em `app/tests/bootstrap_test.py` — adicionar asserção do novo índice `idx_produtos_nome_ativo_unique` (expression index, mesma checagem via `sqlite_master` já usada para o índice equivalente de categoria)
- [x] T002 Adicionar índice único parcial em `Produto.__table_args__` (`app/core/domain/models.py`): `Index("idx_produtos_nome_ativo_unique", text("lower(nome)"), unique=True, postgresql_where=text("ativo = true"), sqlite_where=text("ativo = 1"))`, espelhando `CategoriaProduto` (RF-05, RF-07)

## Fase 2 — Aplicação

- [x] T003 Escrever teste `test_produto_validation_active_duplicate` em `app/tests/core/application/use_cases/produtos_categorias_test.py` — cobre: criar produto com nome já usado por ativo (409 `nome_duplicado`), mesmo nome com case/espaço diferente (409), nome de produto inativo pode ser reaproveitado (201), editar produto para nome de outro ativo (409, nome original preservado), editar produto mantendo o próprio nome (200) (RF-01, RF-02, RF-03, RF-04)
- [x] T004 Adicionar `get_active_by_nome(nome: str, exclude_id: Optional[int] = None) -> Optional[Produto]` ao protocolo `IProdutoRepository` em `app/core/interfaces/adapters/repositories/i_produto_repository.py`
- [x] T005 Implementar `get_active_by_nome` em `app/adapter/repositories/produto_repository.py`, espelhando `CategoriaProdutoRepository.get_active_by_nome` (`func.lower(Produto.nome) == nome.strip().lower()`, `Produto.ativo == True`, exclui `exclude_id` quando informado)
- [x] T006 Implementar `_ensure_nome_disponivel(nome, exclude_id=None)` em `ProdutoService` (`app/core/application/use_cases/produto_service.py`), levantando `ConflictError("nome_duplicado", "Já existe um produto ativo com esse nome")`; chamar em `build()` (sem `exclude_id`), `update()` (com `exclude_id=produto_id`) e `activate()` (com `exclude_id=produto_id` — decisão registrada em `plan.md`, evita reativação recriar duplicidade)

## Fase 3 — Adapters e infra

- [x] T007 Escrever teste `test_rejeita_produto_composto_com_nome_duplicado` em `app/tests/core/application/use_cases/produto_composicao_test.py` — cria produto simples, tenta criar produto composto com o mesmo nome via `/api/produtos/compostos`, espera `409`/`nome_duplicado` e confirma que nenhum produto nem composição são persistidos (RF-06)
- [x] T008 Criar migration Alembic `app/migrations/versions/<nova>_produto_nome_ativo_unique.py`, encadeada em `i9j0k1l2m3n4` (head atual): `upgrade` cria `idx_produtos_nome_ativo_unique` (`sa.text("lower(nome)")`, `unique=True`, `postgresql_where=sa.text("ativo = true")`), `downgrade` remove o índice — espelha exatamente a migration `b2c3d4e5f6a7` para `categoria_produto`
- [x] T009 Rodar os testes de T001, T003 e T007 e confirmar que todos passam com T002, T004-T006, T008 implementados

## Fase 4 — Integração e aceite

> Mesmo desvio já documentado na feature 001 (`specs/001-fiado-avulso-retroativo/plan.md`):
> sem framework BDD no repositório. Os 7 cenários Gherkin de `spec.md` são cobertos pelos
> testes de T003 e T007.

- [x] T010 Atualizar `docs/modules/produtos-categorias.md` — regra de negócio (nome único entre produtos ativos, mesmo padrão de categoria) e novo código de validação reaproveitado (`nome_duplicado` já documentado, mas agora também para produto)
- [x] T011 Atualizar `docs/architecture/errors.md` — nota de que `nome_duplicado` (409) agora também se aplica a produto, não só categoria
- [x] T012 `make validate` verde

## Rastreabilidade

| Requisito | Tarefas |
|---|---|
| RF-01 | T003, T006 |
| RF-02 | T003, T006 |
| RF-03 | T003, T005 |
| RF-04 | T003, T005 |
| RF-05 | T002, T005, T008 |
| RF-06 | T006, T007 |
| RF-07 | T001, T002, T008 |

## Convergence

> Seção **append-only**, escrita por `/bu:converge`. Cada rodada acrescenta um bloco;
> nada é reescrito.

### Rodada 1 — 2026-09-19

| Requisito | Estado | Evidência |
|---|---|---|
| RF-01 (rejeitar cadastro duplicado) | realizado | `produto_service.py::build` chama `_ensure_nome_disponivel`; teste `produtos_categorias_test.py::test_produto_validation_active_duplicate` |
| RF-02 (rejeitar edição duplicada) | realizado | `produto_service.py::update` chama `_ensure_nome_disponivel(exclude_id=produto_id)`; mesmo teste |
| RF-03 (ignorar case/espaço) | realizado | `produto_repository.py::get_active_by_nome` usa `func.lower(...) == nome.strip().lower()`; teste cobre nome em caixa alta com espaços |
| RF-04 (inativo não bloqueia reuso) | realizado | `get_active_by_nome` filtra `ativo == True`; teste cobre reaproveitar nome de produto inativo |
| RF-05 (escopo global) | realizado | Nenhum filtro por `categoria_id` em `get_active_by_nome` nem no índice `idx_produtos_nome_ativo_unique` |
| RF-06 (produto composto também valida) | realizado | `build()` é o único ponto de criação usado por `create()` e `create_composto()`; teste `produto_composicao_test.py::test_rejeita_produto_composto_com_nome_duplicado` confirma que nada é persistido |
| RF-07 (salvaguarda de banco) | realizado | Migration `j0k1l2m3n4o5` cria `idx_produtos_nome_ativo_unique`; `bootstrap_test.py` confirma a criação do índice via schema sqlite |

**Achado durante a implementação, fora do plano original**: `ProdutoService.activate()` também
precisou da checagem (`_ensure_nome_disponivel`), não só `build()`/`update()` — sem isso, a
reativação de um produto cujo nome foi reaproveitado por outro enquanto ele estava inativo
recriaria a duplicidade ativa que a issue #41 pede para bloquear. Decisão e justificativa
registradas em `plan.md` (linha "Proteger `ProdutoService.activate()` também"). Coberto pelo
mesmo teste de T003 (cenário de reativação bloqueada e depois liberada).

**Fora de escopo respeitado**: nenhuma correção de duplicado já existente na base; nenhuma
sugestão automática de nome; a busca por nome (`GET /api/produtos?nome=`) não foi alterada.

**Excesso de escopo**: nenhum, além do achado de `activate()` acima — que não é escopo
adicional, é o mesmo requisito (RF-01/RF-02, "nenhum produto ativo duplicado") aplicado a um
terceiro caminho de mutação que o plano original tinha deixado de fora por engano.

**`make validate`** (`RUN_MIGRATIONS=false`): `141 passed, 4 warnings` — cobertura total
**96.22%** (era 96.21% no baseline da feature 003, antes desta feature).

Veredito: convergido
Tarefas acrescentadas: nenhuma

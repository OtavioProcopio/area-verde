# Tarefas — Validar nome duplicado no cadastro de produto

> Ordem de dependência. `[P]` marca tarefa paralelizável (não toca arquivo de outra `[P]`
> da mesma fase). Teste vem antes da implementação que ele prova.

## Fase 1 — Domínio

- [ ] T001 Estender `test_product_category_indexes_can_be_created` em `app/bootstrap_test.py` — adicionar asserção do novo índice `idx_produtos_nome_ativo_unique` (expression index, mesma checagem via `sqlite_master` já usada para o índice equivalente de categoria)
- [ ] T002 Adicionar índice único parcial em `Produto.__table_args__` (`app/core/domain/models.py`): `Index("idx_produtos_nome_ativo_unique", text("lower(nome)"), unique=True, postgresql_where=text("ativo = true"), sqlite_where=text("ativo = 1"))`, espelhando `CategoriaProduto` (RF-05, RF-07)

## Fase 2 — Aplicação

- [ ] T003 Escrever teste `test_produto_validation_active_duplicate` em `app/produtos_categorias_test.py` — cobre: criar produto com nome já usado por ativo (409 `nome_duplicado`), mesmo nome com case/espaço diferente (409), nome de produto inativo pode ser reaproveitado (201), editar produto para nome de outro ativo (409, nome original preservado), editar produto mantendo o próprio nome (200) (RF-01, RF-02, RF-03, RF-04)
- [ ] T004 Adicionar `get_active_by_nome(nome: str, exclude_id: Optional[int] = None) -> Optional[Produto]` ao protocolo `IProdutoRepository` em `app/core/interfaces/adapters/repositories/i_produto_repository.py`
- [ ] T005 Implementar `get_active_by_nome` em `app/adapter/repositories/produto_repository.py`, espelhando `CategoriaProdutoRepository.get_active_by_nome` (`func.lower(Produto.nome) == nome.strip().lower()`, `Produto.ativo == True`, exclui `exclude_id` quando informado)
- [ ] T006 Implementar `_ensure_nome_disponivel(nome, exclude_id=None)` em `ProdutoService` (`app/core/application/use_cases/produto_service.py`), levantando `ConflictError("nome_duplicado", "Já existe um produto ativo com esse nome")`; chamar em `build()` (sem `exclude_id`) e em `update()` (com `exclude_id=produto_id`)

## Fase 3 — Adapters e infra

- [ ] T007 Escrever teste `test_rejeita_produto_composto_com_nome_duplicado` em `app/produto_composicao_test.py` — cria produto simples, tenta criar produto composto com o mesmo nome via `/api/produtos/compostos`, espera `409`/`nome_duplicado` e confirma que nenhum produto nem composição são persistidos (RF-06)
- [ ] T008 Criar migration Alembic `app/migrations/versions/<nova>_produto_nome_ativo_unique.py`, encadeada em `i9j0k1l2m3n4` (head atual): `upgrade` cria `idx_produtos_nome_ativo_unique` (`sa.text("lower(nome)")`, `unique=True`, `postgresql_where=sa.text("ativo = true")`), `downgrade` remove o índice — espelha exatamente a migration `b2c3d4e5f6a7` para `categoria_produto`
- [ ] T009 Rodar os testes de T001, T003 e T007 e confirmar que todos passam com T002, T004-T006, T008 implementados

## Fase 4 — Integração e aceite

> Mesmo desvio já documentado na feature 001 (`specs/001-fiado-avulso-retroativo/plan.md`):
> sem framework BDD no repositório. Os 7 cenários Gherkin de `spec.md` são cobertos pelos
> testes de T003 e T007.

- [ ] T010 Atualizar `docs/modules/produtos-categorias.md` — regra de negócio (nome único entre produtos ativos, mesmo padrão de categoria) e novo código de validação reaproveitado (`nome_duplicado` já documentado, mas agora também para produto)
- [ ] T011 Atualizar `docs/architecture/errors.md` — nota de que `nome_duplicado` (409) agora também se aplica a produto, não só categoria
- [ ] T012 `make validate` verde

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

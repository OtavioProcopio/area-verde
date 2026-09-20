# Plano de implementação — Validar nome duplicado no cadastro de produto

> Descreve **como**. Deriva da spec e da constituição; não introduz requisito novo.

## Decisões técnicas

| Decisão | Escolha | Alternativas descartadas | Por quê |
|---|---|---|---|
| Padrão de validação | Replicar exatamente o padrão já usado em `CategoriaProdutoService`: checagem de nome ativo na aplicação (`ConflictError` `nome_duplicado`, 409) + índice único parcial no banco (`lower(nome)` onde `ativo`) como salvaguarda | Validar só na aplicação, sem índice de banco | A própria issue #41 pede o índice como salvaguarda, e `CategoriaProduto` já estabelece esse exato padrão dual (`idx_categorias_produto_nome_ativo_unique`) — manter os dois padrões (categoria com salvaguarda, produto sem) seria a inconsistência que a issue aponta |
| Onde entra a checagem de aplicação | Dentro de `ProdutoService.build()` (chamado tanto por `create()` quanto por `ProdutoComposicaoService.create_composto()`) e em `ProdutoService.update()` | Duplicar a checagem em `create()` e em `create_composto()` separadamente | `build()` já é o único ponto por onde toda criação de produto (simples ou composto) passa hoje; checar ali cobre RF-01 e RF-06 com uma só implementação, sem duplicar código |
| Escopo da unicidade | Global entre produtos ativos (RF-05, decidido em `/bu:clarify`) | Unicidade por `categoria_id` | Decisão do usuário; também mantém paridade exata com o índice de categoria, que não tem conceito de escopo |
| Exclusão do próprio produto na edição | `get_active_by_nome(nome, exclude_id=produto_id)`, mesmo parâmetro já usado em `CategoriaProdutoRepository.get_active_by_nome` | Comparar nome antes de persistir sem tocar o repositório | Reaproveita a mesma assinatura/padrão já validado em categoria — não há motivo para uma forma diferente |
| Migration do índice | Nova revisão Alembic, encadeada em `i9j0k1l2m3n4` (head atual), criando `idx_produtos_nome_ativo_unique` com `postgresql_where=ativo = true`, espelhando exatamente a migration de categoria (`b2c3d4e5f6a7`) | Alterar a migration antiga de categoria/produto | Migration já aplicada em ambiente compartilhado não é editada (Princípio "Migrations Alembic" da constituição do projeto) |
| Proteger `ProdutoService.activate()` também | Decisão tomada durante a escrita do teste (T003): sem essa checagem, reativar um produto cujo nome foi "roubado" por outro produto criado enquanto ele estava inativo recriaria a mesma duplicidade ativa que RF-01/RF-02 proíbem, só que pela porta de trás da reativação | Deixar `activate()` sem checagem, como o plano original previa (só `build()`/`update()`) | `CategoriaProdutoService.activate()` já faz exatamente essa checagem hoje (`_ensure_active_nome_available(categoria.nome, exclude_id=categoria_id)`); não replicar para produto deixaria uma forma real e fácil de burlar a validação, contrariando o próprio objetivo da spec |

## Padrões de projeto aplicados

| Padrão | Onde | Problema que resolve | Custo aceito |
|---|---|---|---|
| — | — | — | — |

Nenhum padrão GoF novo: é a mesma checagem condicional já usada em `CategoriaProdutoService`,
replicada por consistência (Princípio "Simplicidade defensável" — YAGNI/DRY não pedem uma
abstração comum entre as duas checagens hoje, já que são pequenas e specíficas de cada entidade;
criar uma abstração compartilhada agora seria antecipação sem um terceiro caso de uso real).

## Arquivos a criar ou alterar

| Camada | Arquivo | Ação | Teste espelhado |
|---|---|---|---|
| core/domain | `app/core/domain/models.py` | alterar — novo índice único parcial em `Produto.__table_args__` | `app/tests/bootstrap_test.py::test_product_category_indexes_can_be_created` (estender) |
| core/interfaces | `app/core/interfaces/adapters/repositories/i_produto_repository.py` | alterar — novo método `get_active_by_nome` no protocolo | — (protocolo, sem lógica) |
| adapters/repositories | `app/adapter/repositories/produto_repository.py` | alterar — implementar `get_active_by_nome`, espelhando `CategoriaProdutoRepository.get_active_by_nome` | `app/tests/core/application/use_cases/produtos_categorias_test.py` (exercitado via serviço/API, mesma convenção já usada para o equivalente de categoria) |
| core/application | `app/core/application/use_cases/produto_service.py` | alterar — `_ensure_nome_disponivel` chamado em `build()`, `update()` e `activate()` | `app/tests/core/application/use_cases/produtos_categorias_test.py` |
| adapters/repositories | `app/migrations/versions/<nova>_produto_nome_ativo_unique.py` | criar — índice único parcial `idx_produtos_nome_ativo_unique` | `app/tests/bootstrap_test.py::test_product_category_indexes_can_be_created` (mesma extensão acima) |
| testes | `app/tests/core/application/use_cases/produtos_categorias_test.py` | alterar — novo teste `test_produto_validation_active_duplicate` | — (é o próprio teste) |
| testes | `app/tests/core/application/use_cases/produto_composicao_test.py` | alterar — novo teste `test_rejeita_produto_composto_com_nome_duplicado` | — (é o próprio teste) |
| docs | `docs/modules/produtos-categorias.md` | alterar — regra de negócio e validação nova | — |
| docs | `docs/architecture/errors.md` | alterar — `nome_duplicado` já existe para categoria; documentar que agora também se aplica a produto | — |
| docs | `docs/policies/migration-policy.md` referência | nenhuma alteração de conteúdo, só a migration em si segue a política já documentada | — |

Nenhum arquivo novo em `core/interfaces` fora do protocolo já existente, nenhum DTO novo:
`nome_duplicado` já é código de erro existente (`docs/architecture/errors.md`), e os DTOs de
request de produto (`ProdutoRequest`) não mudam de formato.

## Contrato entre camadas

`ProdutoService._ensure_nome_disponivel(nome, exclude_id=None)`:
1. Normaliza o nome (`strip()`, comparação `lower()` já é feita no repositório).
2. Chama `produto_repository.get_active_by_nome(nome, exclude_id=exclude_id)`.
3. Se encontrar produto ativo diferente do excluído, levanta `ConflictError("nome_duplicado",
   "Já existe um produto ativo com esse nome")` (409) — mesma mensagem/padrão de categoria.

`build()` chama `_ensure_nome_disponivel(nome)` sem `exclude_id` (sempre criação nova) — cobre
`create()` (produto simples) e `create_composto()` (produto composto), já que ambos chamam
`build()` antes de persistir.

`update()` chama `_ensure_nome_disponivel(nome, exclude_id=produto_id)` — permite manter o
próprio nome e bloqueia usar o nome de outro produto ativo.

O índice único do banco (`idx_produtos_nome_ativo_unique`) é salvaguarda: em uso normal, a
checagem da aplicação intercepta antes. Uma violação do índice geraria `IntegrityError` do
SQLAlchemy — fora do escopo desta feature tratar esse caso especificamente (mesmo estado atual
de categoria, que também não trata `IntegrityError` desse índice em código de aplicação).

## Dependências externas

| Dependência | Versão | Justificativa | Simulada nos testes por |
|---|---|---|---|
| — | — | Nenhuma dependência nova | Banco sqlite em memória via `app/conftest.py`, mesma convenção já usada |

## Impacto no contrato de operação

Nenhum alvo de `Makefile` novo. A migration nova é aplicada pelo fluxo já existente
(`RUN_MIGRATIONS`/`alembic upgrade head` em `infra/config/database.py`), sem mudança de
contrato.

## Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Ambiente com produtos ativos já duplicados hoje (a própria issue #41 relata que isso ocorreu em teste real de uso) faz a migration falhar ao criar o índice único | Média | Aceito deliberadamente: `spec.md` lista "unificar ou mesclar produtos já duplicados hoje" como **fora de escopo** — a migration não decide sozinha qual duplicado desativar (arriscaria esconder produto referenciado em comanda/estoque). Se a migration falhar por dado existente, quem aplica resolve manualmente antes (mesma postura de qualquer `UniqueConstraint`/`CHECK` novo sobre dado pré-existente) — não é regressão introduzida por este plano, é a política de migration do projeto já em vigor |
| Índice único global impedir um caso legítimo de nome igual em categorias diferentes que o usuário não previu | Baixa (decisão do usuário em `/bu:clarify` foi explícita por escopo global) | Nenhuma — é a regra pedida; documentado em `spec.md` |

## Conformidade com a constituição

| Princípio | Como este plano o respeita |
|---|---|
| Contrato de operação | Nenhum alvo de `Makefile` novo; migration aplicada pelo fluxo já existente; testes rodam por `make test`/`make test-coverage` |
| Arquitetura limpa | `core/application` (`ProdutoService`) não importa `adapters`; `core/interfaces` ganha só a assinatura do método novo; `adapters/repositories` implementa a consulta. Segue a mesma estrutura pré-existente já documentada como desvio aceito do template da organização (`app/core/interfaces/...`, não `app/interfaces/...` — ver `plan.md` da feature 001) |
| Testes provam a entrega | Todo cenário de aceite da spec vira `test_deve_<resultado>_quando_<condição>`-style em `app/tests/core/application/use_cases/produtos_categorias_test.py`/`app/tests/core/application/use_cases/produto_composicao_test.py`, convenção já usada (TestClient + sqlite em memória); cobertura mínima 90% nos arquivos modificados |
| Simplicidade defensável | Reaproveita 100% do padrão já validado em `CategoriaProdutoService`/`CategoriaProdutoRepository`; nenhum padrão GoF novo, nenhuma abstração compartilhada prematura |
| Autoria | Nenhum artefato atribui autoria a ferramenta de IA |
| Idioma | `spec.md`, este `plan.md`, mensagens de erro e documentação em português |
| Migrations Alembic (específico do projeto) | Migration nova, não edita nenhuma migration já aplicada; `upgrade`/`downgrade` coerentes, escopo restrito ao índice de `produto` |

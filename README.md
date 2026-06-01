<p align="center">
  <h1 align="center">Area Verde API</h1>
</p>

<p align="center">
  API para MVP de controle operacional de bar: produtos simples e compostos,
  estoque, comandas, pagamentos, fiado, caixa e relatórios.
</p>

<p align="center">
  <a href="docs/README.md"><img src="https://img.shields.io/badge/docs-portal-2ea44f" alt="Documentação"></a>
  <a href="docs/policies/git-flow-policy.md"><img src="https://img.shields.io/badge/git--flow-develop%20%2B%20main-blue" alt="Git Flow"></a>
  <a href="app/pytest.ini"><img src="https://img.shields.io/badge/tests-pytest-0a7" alt="Pytest"></a>
  <a href="app/pyproject.toml"><img src="https://img.shields.io/badge/code%20style-black-000" alt="Black"></a>
  <a href="app/Dockerfile"><img src="https://img.shields.io/badge/docker-ready-2496ed" alt="Docker"></a>
  <img src="https://img.shields.io/badge/status-MVP%20em%20constru%C3%A7%C3%A3o-f59e0b" alt="Status do MVP">
</p>

<p align="center">
  <a href="#mapa-do-projeto">Mapa</a>
  ·
  <a href="#funcionalidades">Funcionalidades</a>
  ·
  <a href="#quickstart">Quickstart</a>
  ·
  <a href="#documenta%C3%A7%C3%A3o">Documentação</a>
  ·
  <a href="#contribui%C3%A7%C3%A3o">Contribuição</a>
</p>

## Mapa do projeto

| Área | Atalho | Para quê serve |
|---|---|---|
| Produto e estoque | [Produtos](docs/modules/produtos-categorias.md) · [Estoque](docs/modules/estoque.md) | Cadastro vendável, composição e controle operacional |
| Atendimento | [Clientes](docs/modules/clientes.md) · [Comandas](docs/modules/comandas.md) | Cadastro simples, lançamento de consumo e baixa automática |
| Financeiro | [Pagamentos](docs/modules/pagamentos.md) · [Caixa](docs/modules/caixa.md) · [Fiado](docs/modules/fiado.md) | Fechamento, caixa diário e pendências futuras |
| Gestão | [Relatórios](docs/modules/relatorios.md) · [Configurações](docs/modules/configuracoes.md) | Consolidação e parâmetros do sistema |
| Engenharia | [Arquitetura](docs/architecture/architecture.md) · [Testes](docs/architecture/tests.md) · [Policies](docs/policies/) | Padrões para humanos e agentes |
| Operação local | [Make](docs/workflows/makefile.md) · [Postman](docs/postman/README.md) · [Workflows](docs/workflows/README.md) | Automação, testes manuais e rotina de desenvolvimento |

## Funcionalidades

### Implementado

| Módulo | O que já faz | Documentação |
|---|---|---|
| Produtos e Categorias | Cadastra categorias, produtos simples, produtos compostos e composição | [Abrir](docs/modules/produtos-categorias.md) |
| Estoque | Consulta estoque, registra entrada/ajuste, lista movimentos e consumo por componente | [Abrir](docs/modules/estoque.md) |
| Comandas e Itens | Abre comanda, lança itens simples/compostos, recalcula total e movimenta estoque | [Abrir](docs/modules/comandas.md) |
| Pagamentos e Fechamento | Fecha comanda aberta, registra pagamento e bloqueia alterações posteriores | [Abrir](docs/modules/pagamentos.md) |
| Caixa Diário | Abre caixa, registra reforço/sangria, vincula pagamentos e fecha com conferência | [Abrir](docs/modules/caixa.md) |
| Clientes | Cadastra, lista, edita, ativa e inativa clientes para histórico de pendências | [Abrir](docs/modules/clientes.md) |
| Fiado / Pendências | Marca comanda como pendente, lista vencidos e quita no caixa aberto | [Abrir](docs/modules/fiado.md) |
| Relatórios | Consolida diário, caixa, produtos vendidos, consumo de estoque, fiados, estoque e comandas | [Abrir](docs/modules/relatorios.md) |
| Configurações | Mantém parâmetros operacionais, prazo padrão do fiado e regra de estoque negativo | [Abrir](docs/modules/configuracoes.md) |
| Acesso / Senha | Valida senha simples do MVP e permite definir/alterar hash operacional | [Abrir](docs/modules/acesso.md) |

### Pendente

| Módulo | Próximo papel no MVP | Documentação |
|---|---|---|
| Release MVP | Consolidar validações finais e documentação de entrega | [Roadmap](docs/roadmap.md) |
| Frontend | Operação visual do bar | [Roadmap](docs/roadmap.md) |

## Stack

| Camada | Tecnologias |
|---|---|
| API | Python, FastAPI |
| Domínio e dados | SQLModel, PostgreSQL, Alembic |
| Arquitetura | Clean Architecture, Dependency Injector |
| Qualidade | Pytest, Black, Isort, Flake8, Mypy |
| Ambiente | Docker, Docker Compose, DevContainer |
| Entrega | GitHub Actions, Git Flow |

## Quickstart

### Rodar localmente

```bash
cd app
make install
make run
```

API local:

```text
http://localhost:8001
```

### Rodar com Docker

```bash
cp app/.env.example app/.env
cd app
make docker-build
make up
```

API via Docker Compose:

```text
http://localhost:58001
```

### Validar

```bash
cd app
make validate
```

Validação somente leitura:

```bash
make check
```

## Documentação

| Tema | Link |
|---|---|
| Portal completo | [docs/README.md](docs/README.md) |
| Visão geral | [docs/overview.md](docs/overview.md) |
| Roadmap | [docs/roadmap.md](docs/roadmap.md) |
| Matriz funcional | [docs/matrix/functional-coverage.md](docs/matrix/functional-coverage.md) |
| Endpoints por módulo | [docs/matrix/endpoints-by-module.md](docs/matrix/endpoints-by-module.md) |
| Pendências e lacunas | [docs/matrix/pending-gaps.md](docs/matrix/pending-gaps.md) |
| Glossário | [docs/glossary.md](docs/glossary.md) |
| Arquitetura | [docs/architecture/architecture.md](docs/architecture/architecture.md) |
| Camadas | [docs/architecture/layers.md](docs/architecture/layers.md) |
| Banco e migrations | [docs/architecture/database.md](docs/architecture/database.md) |
| Erros | [docs/architecture/errors.md](docs/architecture/errors.md) |
| Testes | [docs/architecture/tests.md](docs/architecture/tests.md) |
| Comandos Make | [docs/workflows/makefile.md](docs/workflows/makefile.md) |
| Preflight | [docs/policies/preflight-policy.md](docs/policies/preflight-policy.md) |
| Migrations | [docs/policies/migration-policy.md](docs/policies/migration-policy.md) |
| Documentação | [docs/policies/documentation-policy.md](docs/policies/documentation-policy.md) |
| Review | [docs/policies/review-policy.md](docs/policies/review-policy.md) |
| Diagramas | [docs/diagrams/README.md](docs/diagrams/README.md) |
| Postman | [docs/postman/README.md](docs/postman/README.md) |

## Contribuição

Antes de abrir PR:

- Execute o [Preflight obrigatório](docs/policies/preflight-policy.md).
- Siga a [Git Flow Policy](docs/policies/git-flow-policy.md).
- Use a [Branch Policy](docs/policies/branch-policy.md).
- Escreva commits conforme a [Commit Policy](docs/policies/commit-policy.md).
- Abra PR seguindo a [Pull Request Policy](docs/policies/pull-request-policy.md).
- Atualize documentação conforme a [Documentation Policy](docs/policies/documentation-policy.md).
- Trate migrations conforme a [Migration Policy](docs/policies/migration-policy.md).
- Não commite secrets: [Security Policy](docs/policies/security-policy.md).

Fluxo padrão:

```bash
git status
git fetch origin
git checkout develop
git pull origin develop
git checkout -b feature/nome-do-modulo
```

## Git Flow

| Branch | Papel |
|---|---|
| `main` | Linha estável |
| `develop` | Integração |
| `feature/*` | Novas funcionalidades |
| `bugfix/*` | Correções comuns |
| `docs/*` | Documentação |
| `release/*` | Preparação de versão |
| `hotfix/*` | Correções urgentes |

Não trabalhe direto em `main` ou `develop`. Integre mudanças via Pull Request.

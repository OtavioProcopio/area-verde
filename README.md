# Area Verde API

API para MVP de controle operacional de bar, com foco em produtos, estoque,
comandas, pagamentos, fiado, caixa e relatórios.

## Estado atual

| Módulo | Status |
|---|---|
| Produtos e Categorias | Implementado |
| Estoque | Implementado |
| Comandas e Itens | Implementado |
| Pagamentos e Fechamento | Pendente |
| Fiado / Pendências | Pendente |
| Caixa Diário | Pendente |
| Relatórios | Pendente |
| Configurações | Pendente |
| Acesso / Senha | Pendente |

## Stack

- Python
- FastAPI
- SQLModel
- Alembic
- PostgreSQL
- Dependency Injector
- Docker e Docker Compose
- DevContainer
- Pytest
- Black, Isort, Flake8 e Mypy
- GitHub Actions
- Git Flow

## Como rodar localmente

Execute os comandos dentro da pasta `app/`.

```bash
cd app
make install
make run
```

A API local fica disponível em `http://localhost:8001`.

## Como rodar com Docker

Crie o arquivo de ambiente a partir do exemplo:

```bash
cp app/.env.example app/.env
```

Depois suba os containers:

```bash
cd app
make docker-build
make up
```

Com Docker Compose, a API fica disponível em `http://localhost:58001`.

## Como rodar testes

```bash
cd app
make build
make test
make lint
```

Validações diretas equivalentes:

```bash
python -m py_compile api.py
pytest . -v -m "not integration"
black --check .
isort --check-only .
flake8 --max-line-length=88 --exclude=.venv .
mypy --ignore-missing-imports --explicit-package-bases .
```

## Documentação

Veja o índice em [docs/README.md](docs/README.md).

## Como contribuir

Leia [CONTRIBUTING.md](CONTRIBUTING.md) e as policies em
[docs/policies/](docs/policies/).

## Git Flow

- `main`: branch estável.
- `develop`: branch de integração.
- `feature/*`: novas funcionalidades.
- `bugfix/*`: correções comuns.
- `release/*`: preparação de versão.
- `hotfix/*`: correções urgentes em produção.

Não trabalhe direto em `main` ou `develop`. Abra Pull Requests para integrar
alterações.

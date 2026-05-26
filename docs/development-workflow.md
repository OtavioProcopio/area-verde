# Workflow de Desenvolvimento

Este guia descreve a rotina diária de trabalho no Area Verde API.

## Branch base

Use `develop` como base para todo desenvolvimento comum:

```bash
git checkout develop
git pull origin develop
```

Crie uma branch curta e objetiva:

```bash
git checkout -b feature/comandas
```

ou:

```bash
git checkout -b bugfix/corrigir-total-comanda
```

## Antes de abrir Pull Request

Rode as validações locais dentro de `app/`:

```bash
make build
make test
make lint
```

Se estiver trabalhando só com Docker:

```bash
POSTGRES_PASSWORD=local-dev-only docker compose config
docker build -t area-verde-api-test .
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api python -m pytest . -v -m "not integration"
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api black --check .
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api isort --check-only .
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api flake8 --max-line-length=88 --exclude=.venv .
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api mypy --ignore-missing-imports --explicit-package-bases .
docker compose down
```

## Pull Requests

- PRs de `feature/*` e `bugfix/*` devem ir para `develop`.
- PRs para `main` devem vir apenas de `release/*` ou `hotfix/*`.
- O merge só deve acontecer se build, testes, lint e type check passarem.
- Resolva conflitos antes de pedir revisão final.

## Banco de dados

O projeto usa PostgreSQL via Docker Compose e Alembic para migrations.

Para subir localmente:

```bash
cd app
cp .env.example .env
# preencha POSTGRES_PASSWORD em .env
docker compose up -d
```

Para aplicar migrations no container:

```bash
docker compose exec api alembic upgrade head
```

Não faça alterações manuais de schema sem migration.

## Segurança

Nunca commite:

- `.env` real;
- senhas;
- tokens;
- certificados;
- chaves privadas;
- secrets de deploy.

Use `app/.env.example` apenas como referência segura.

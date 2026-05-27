# Workflow de Desenvolvimento

Este guia descreve a rotina diária de trabalho no Area Verde API.

## Branch base

Use `develop` como base para todo desenvolvimento comum:

```bash
git status
git fetch origin
git checkout develop
git pull origin develop
git checkout -b feature/nome-da-feature
```

Use o prefixo correto para o tipo de tarefa:

```bash
git checkout -b bugfix/corrigir-total-comanda
git checkout -b docs/atualiza-politicas
```

## Antes de abrir Pull Request

Rode as validações recomendadas dentro de `app/`:

```bash
cd app
make validate
make ci
git diff --check
```

## Validações Docker

Se estiver dentro do DevContainer e não houver binário `docker`, execute no host:

```bash
cd app
POSTGRES_PASSWORD=local-dev-only docker compose config
docker build -t area-verde-api-test .
```

Informe na PR se cada validação foi executada no DevContainer ou no host.

## Antes de pedir revisão

```bash
git status
git branch --show-current
git log --oneline --decorate -5
```

Confirme:

- branch não é `main`;
- branch não é `develop`;
- branch nasceu da `develop` atualizada;
- PR será aberta para `develop`.

## Pull Requests

- PRs de `feature/*`, `bugfix/*` e `docs/*` devem ir para `develop`.
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

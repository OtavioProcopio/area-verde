# Contribuindo com o Area Verde API

Este projeto usa Git Flow, Pull Requests obrigatórios e Conventional Commits.
A branch principal de desenvolvimento é `develop`; a branch estável é `main`.

## Padrão de branches

- `feature/*`: novas funcionalidades, sempre a partir de `develop`.
- `bugfix/*`: correções normais, sempre a partir de `develop`.
- `release/*`: preparação de versão, sempre a partir de `develop`.
- `hotfix/*`: correções urgentes, sempre a partir de `main`.

Exemplo para nova funcionalidade:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/comandas
```

Exemplo para correção normal:

```bash
git checkout develop
git pull origin develop
git checkout -b bugfix/corrigir-total-comanda
```

## Padrão de commits

Use Conventional Commits:

```bash
feat: adiciona criação de comanda
fix: corrige cálculo do total da comanda
docs: adiciona documentação do fluxo git
test: adiciona testes de produto
refactor: reorganiza camada de serviço
chore: configura pipeline de CI
ci: adiciona workflow do GitHub Actions
```

## Pull Requests

- Não envie código direto para `main`.
- Não envie código direto para `develop`, exceto setup inicial combinado.
- Abra PR para `develop` ao concluir `feature/*` ou `bugfix/*`.
- Abra PR para `main` apenas a partir de `release/*` ou `hotfix/*`.
- Aguarde CI completo antes do merge.

## Checklist

- [ ] Código compila
- [ ] Testes passam localmente
- [ ] Não há arquivos sensíveis commitados
- [ ] Não há alterações fora do escopo
- [ ] Documentação atualizada, se necessário
- [ ] Migrations revisadas, se houver banco de dados

## Como rodar testes localmente

Pelo DevContainer ou ambiente local:

```bash
cd app
make install
make test
make lint
make build
```

Pelo Docker, sem depender do Python local:

```bash
cd app
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api python -m pytest . -v -m "not integration"
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api black --check .
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api isort --check-only .
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api flake8 --max-line-length=88 --exclude=.venv .
POSTGRES_PASSWORD=local-dev-only docker compose run --rm -e RUN_MIGRATIONS=false api mypy --ignore-missing-imports --explicit-package-bases .
docker compose down
```

## Preparar release

O versionamento segue SemVer (`MAJOR.MINOR.PATCH`).

```bash
git checkout develop
git pull origin develop
git checkout -b release/v0.1.0
```

Na release:

- corrigir bugs finais;
- atualizar documentação;
- revisar migrations;
- garantir que CI passa;
- abrir PR de `release/v0.1.0` para `main`;
- depois abrir PR de `release/v0.1.0` para `develop`, se houve ajustes na release.

Após merge em `main`:

```bash
git checkout main
git pull origin main
git tag v0.1.0
git push origin v0.1.0
```

## Hotfix

```bash
git checkout main
git pull origin main
git checkout -b hotfix/corrigir-problema-x
```

Depois:

1. Corrija o problema.
2. Abra PR para `main`.
3. Após merge, gere uma nova tag patch, por exemplo `v0.1.1`.
4. Abra PR do hotfix para `develop`.

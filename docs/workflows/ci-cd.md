# CI/CD

Este repositório possui workflows conservadores de integração e entrega
contínua. Nenhum deploy real é executado enquanto não houver ambiente definido.

## CI

Arquivo:

```text
.github/workflows/ci.yml
```

Gatilhos:

- Pull Request para `develop` e `main`.
- Push para `develop`, `main`, `feature/**`, `bugfix/**`, `docs/**` e `chore/**`.

Validações (job `validate`):

- instala dependências Python;
- compila `api.py`;
- executa `black --check`;
- executa `isort --check-only`;
- executa `flake8`;
- executa `mypy`;
- executa testes com `pytest`;
- valida `docker compose config`;
- valida build da imagem Docker.

PRs para `main` têm regra extra: a branch origem deve ser `release/vMAJOR.MINOR.PATCH`
ou `hotfix/*`.

### Abertura automática de PR (job `open-pr`)

Quando um push acontece em uma branch `feature/*`, `bugfix/*`, `docs/*` ou `chore/*` e o
job `validate` passa, o job `open-pr` abre automaticamente uma Pull Request
dessa branch para `develop`, seguindo a [Git Flow Policy](../policies/git-flow-policy.md).
Se já existir uma PR aberta com o mesmo `head` e `base`, nada é criado
novamente — o job apenas confirma que a PR já existe.

## CD preparatório

Arquivo:

```text
.github/workflows/cd.yml
```

Gatilhos:

- push em `develop`;
- push em `main`;
- tags `v*.*.*`.

O workflow:

- valida tag semântica quando o gatilho for tag;
- instala dependências;
- executa build check e testes;
- valida Docker Compose;
- builda a imagem Docker sem publicar;
- gera artefato `.tar.gz`;
- publica o artefato no GitHub Actions.

## Ambientes planejados

- `development`: builds vindos de `develop`.
- `staging`: reservado para homologação futura.
- `production`: builds vindos de `main` e tags versionadas.

## Secrets futuros

Não há deploy real configurado. Quando houver ambiente definido, estes secrets
devem ser criados no GitHub:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `CONTAINER_REGISTRY`
- `CONTAINER_REGISTRY_USER`
- `CONTAINER_REGISTRY_TOKEN`
- `DATABASE_URL` ou variáveis equivalentes de banco
- `POSTGRES_PASSWORD`

Não crie secrets fictícios e não coloque credenciais reais em arquivos do
repositório.

## Banco no CI

O CI não depende de banco externo real. As validações usam variáveis efêmeras do
próprio workflow para validar Docker Compose e manter os testes unitários sem
conexão externa.

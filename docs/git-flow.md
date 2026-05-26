# Git Flow

Este repositório usa um fluxo baseado em Git Flow para manter o MVP organizado,
com integração contínua em `develop` e estabilidade em `main`.

## Branches

- `main`: código estável, pronto para produção.
- `develop`: branch principal de integração do desenvolvimento.
- `feature/*`: novas funcionalidades.
- `bugfix/*`: correções normais.
- `release/*`: preparação de versões.
- `hotfix/*`: correções urgentes vindas da `main`.

## Funcionalidades

Toda nova funcionalidade deve sair de `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/comandas
```

Ao finalizar, abra Pull Request para `develop`.

## Correções normais

Toda correção normal deve sair de `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b bugfix/corrigir-total-comanda
```

Ao finalizar, abra Pull Request para `develop`.

## Releases

Toda versão de entrega deve sair de `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b release/v0.1.0
```

Durante a release:

- corrigir bugs finais;
- atualizar documentação;
- revisar migrations;
- garantir que CI passa;
- abrir PR de `release/v0.1.0` para `main`;
- abrir PR de `release/v0.1.0` para `develop`, se houve ajustes na release.

Após merge em `main`:

```bash
git checkout main
git pull origin main
git tag v0.1.0
git push origin v0.1.0
```

## Hotfixes

Hotfix deve sair de `main`:

```bash
git checkout main
git pull origin main
git checkout -b hotfix/corrigir-fechamento-caixa
```

Depois:

1. Corrigir o problema.
2. Abrir PR para `main`.
3. Após merge, gerar nova tag patch, por exemplo `v0.1.1`.
4. Abrir PR para `develop`.

## Versionamento

Este projeto usa versionamento semântico:

```text
MAJOR.MINOR.PATCH
```

- `PATCH`: correções.
- `MINOR`: novas funcionalidades compatíveis.
- `MAJOR`: mudanças incompatíveis ou grandes quebras.

Para o MVP, a primeira versão planejada é:

```text
v0.1.0
```

## Conventional Commits

Exemplos aceitos:

```bash
feat: adiciona criação de comanda
fix: corrige cálculo do total da comanda
docs: adiciona documentação do fluxo git
test: adiciona testes de produto
refactor: reorganiza camada de serviço
chore: configura pipeline de CI
ci: adiciona workflow do GitHub Actions
```

## Proteção de branches no GitHub

Configure manualmente no GitHub.

### `main`

- bloquear push direto;
- exigir Pull Request;
- exigir status checks do CI;
- exigir branch atualizada antes do merge;
- impedir force push;
- impedir deleção da branch;
- permitir merge apenas de `release/*` ou `hotfix/*`, como regra operacional.

### `develop`

- evitar push direto;
- exigir Pull Request;
- exigir CI passando;
- impedir force push;
- impedir deleção da branch.

## Primeiro push da `develop`

A branch local `develop` deve ser publicada uma vez:

```bash
git push -u origin develop
```

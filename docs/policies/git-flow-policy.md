# Git Flow Policy

## Branches principais

- `main`: branch estável.
- `develop`: branch de integração.

## Branches de trabalho

- `feature/*`: novas funcionalidades.
- `bugfix/*`: correções comuns.
- `docs/*`: documentação.
- `release/*`: preparação para `main`.
- `hotfix/*`: correções urgentes em `main`.

## Regras

- `feature/*` sempre nasce de `develop`.
- `feature/*` sempre abre PR para `develop`.
- `bugfix/*` sempre nasce de `develop`.
- `bugfix/*` sempre abre PR para `develop`.
- `docs/*` sempre nasce de `develop`.
- `docs/*` sempre abre PR para `develop`.
- `develop` não deve ir direto para `main`.
- `main` só recebe PR de `release/*` ou `hotfix/*`.
- Não trabalhar direto em `main`.
- Não trabalhar direto em `develop`.
- Toda feature deve nascer da `develop` atualizada, não apenas de uma `develop` local antiga.

## Criando uma feature corretamente

```bash
git fetch origin
git checkout develop
git pull origin develop
git checkout -b feature/nome-da-feature
```

## Abrindo PR corretamente

```text
feature/nome-da-feature -> develop
```

## Fluxos proibidos

- `feature/* -> main`
- `docs/* -> main`
- `bugfix/* -> main`
- `develop -> main` diretamente.
- `main -> feature/*`
- `branch antiga -> feature nova`

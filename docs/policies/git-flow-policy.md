# Git Flow Policy

## Branches principais

- `main`: branch estável.
- `develop`: branch de integração.

## Branches de trabalho

- `feature/*`: novas funcionalidades.
- `bugfix/*`: correções comuns.
- `release/*`: preparação para `main`.
- `hotfix/*`: correções urgentes em `main`.

## Regras

- `feature/*` sempre nasce de `develop`.
- `feature/*` sempre abre PR para `develop`.
- `bugfix/*` sempre nasce de `develop`.
- `bugfix/*` sempre abre PR para `develop`.
- `develop` não deve ir direto para `main`.
- `main` só recebe PR de `release/*` ou `hotfix/*`.
- Não trabalhar direto em `main`.
- Não trabalhar direto em `develop`.

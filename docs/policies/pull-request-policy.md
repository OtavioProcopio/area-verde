# Pull Request Policy

## Regras

- PR deve ter objetivo claro.
- PR deve listar funcionalidades ou alterações.
- PR deve listar validações executadas.
- PR deve ser pequena e focada.
- PR deve passar no CI.
- PR para `develop` deve vir de `feature/*`, `bugfix/*`, `docs/*` ou `chore/*`.
- PR para `main` deve vir de `release/*` ou `hotfix/*`.
- Se a PR foi aberta com base errada, não corrigir via merge. Fechar ou retargetar a PR antes da revisão.

## Base correta da PR

| Branch de origem | Base correta |
|---|---|
| `feature/*` | `develop` |
| `bugfix/*` | `develop` |
| `docs/*` | `develop` |
| `chore/*` | `develop` |
| `release/*` | `main` |
| `hotfix/*` | `main` |

Antes de abrir a PR, confirmar:

```text
base: develop
compare: feature/* | bugfix/* | docs/*
```

Para features comuns, se a base for `main`, a PR está errada.

## Checklist obrigatório da PR

- [ ] Branch nasceu de `develop`.
- [ ] `develop` foi atualizado antes da branch.
- [ ] PR está apontando para `develop`.
- [ ] CI passou.
- [ ] `make validate` foi executado.
- [ ] `git diff --check` foi executado.
- [ ] Docker Compose config foi validado.
- [ ] Docker build foi validado.
- [ ] Documentação foi atualizada quando necessário.
- [ ] Nenhum secret foi commitado.
- [ ] Nenhuma migration antiga foi alterada indevidamente.

## Template sugerido

```markdown
## Objetivo

## Funcionalidades

## Validações executadas

- [ ] Build
- [ ] Testes
- [ ] Lint
- [ ] Type check
- [ ] Docker Compose config
- [ ] Docker build

## Observações
```

## Antes de abrir PR

- Revise o diff.
- Confirme que não há secrets.
- Confirme que a branch base está correta.
- Confirme que documentação foi atualizada quando necessário.

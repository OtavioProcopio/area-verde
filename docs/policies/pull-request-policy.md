# Pull Request Policy

## Regras

- PR deve ter objetivo claro.
- PR deve listar funcionalidades ou alterações.
- PR deve listar validações executadas.
- PR deve ser pequena e focada.
- PR deve passar no CI.
- PR para `develop` deve vir de `feature/*`, `bugfix/*` ou `docs/*`.
- PR para `main` deve vir de `release/*` ou `hotfix/*`.

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

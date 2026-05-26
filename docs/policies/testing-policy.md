# Testing Policy

## Regras

- Toda feature deve ter teste.
- Testar fluxo positivo e negativo.
- Testar validações.
- Testar erro esperado.
- Testar integração entre módulos quando aplicável.
- Não criar teste falso.
- Não pular teste sem justificativa.
- Não fazer merge com teste falhando.

## Comandos

Execute dentro de `app/`:

```bash
pytest . -v -m "not integration"
black --check .
isort --check-only .
flake8 --max-line-length=88 --exclude=.venv .
mypy --ignore-missing-imports --explicit-package-bases .
```

## Cobertura esperada

- Endpoints públicos.
- Services/use cases.
- Validações de domínio.
- Persistência e efeitos colaterais relevantes.
- Movimentos de estoque quando houver integração com estoque.

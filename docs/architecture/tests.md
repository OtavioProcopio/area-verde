# Testes

## Ferramentas

- Pytest
- FastAPI TestClient
- SQLite em memória nos testes locais
- Fixtures `test_engine`, `test_session` e `test_container`

## Padrão de arquivos

Os testes ficam em `app/` com sufixo `_test.py`.

Exemplos:

- `produtos_categorias_test.py`
- `estoque_test.py`
- `comandas_test.py`

## O que testar

- Fluxos positivos.
- Fluxos negativos.
- Validações de entrada.
- Erros esperados.
- Integração entre módulos quando aplicável.
- Persistência relevante.

## Comandos

Execute dentro de `app/`:

```bash
pytest . -v -m "not integration"
black --check .
isort --check-only .
flake8 --max-line-length=88 --exclude=.venv .
mypy --ignore-missing-imports --explicit-package-bases .
```

## Regras

- Não criar teste falso apenas para passar pipeline.
- Não pular teste sem justificativa clara.
- Não fazer merge com teste falhando.
- Teste deve descrever comportamento de negócio observável.

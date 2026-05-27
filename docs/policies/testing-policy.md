# Testing Policy

## Regras

- Toda feature deve ter teste.
- Toda nova regra de negócio precisa de teste positivo e negativo.
- Toda integração entre módulos precisa de teste de regressão.
- Toda mudança em status de entidade precisa testar bloqueios posteriores.
- Testar validações.
- Testar erro esperado.
- Testar integração entre módulos quando aplicável.
- Não criar teste falso.
- Não pular teste sem justificativa.
- Não fazer merge com teste falhando.

## Exemplos do sistema

- Comanda fechada não pode receber item.
- Pagamento não deve baixar estoque novamente.
- Caixa fechado não deve aceitar sangria/reforço.

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

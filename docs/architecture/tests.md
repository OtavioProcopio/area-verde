# Testes

## Ferramentas

- Pytest
- FastAPI TestClient
- SQLite em memória nos testes locais
- Fixtures `test_engine`, `test_session` e `test_container`

## Padrão de arquivos

Os testes ficam em `app/` com sufixo `_test.py`.

## Cobertura por modulo

| Modulo | Arquivo principal | Cobertura |
|---|---|---|
| Health | `health_test.py` | Endpoint de saude |
| Bootstrap / Infra | `bootstrap_test.py` | Criacao da app, schema e container |
| Produtos e Categorias | `produtos_categorias_test.py` | Ciclo de vida, filtros e validacoes |
| Estoque | `estoque_test.py` | Consultas, entrada, ajuste e historico |
| Comandas e Itens | `comandas_test.py` | Criacao, itens, estoque e cancelamento |
| Pagamentos e Fechamento | `pagamentos_test.py` | Fechamento, pagamentos e regressao de status |
| Caixa Diario | `caixa_test.py` | Abertura, movimentacoes, pagamentos e fechamento |
| Clientes | `clientes_test.py` | Cadastro, filtros, ativacao, inativacao e duplicidade |
| Fiado / Pendencias | `fiado_test.py` | Pendencias, vencidos, quitacao e cliente inativo |
| Relatorios basicos | `relatorios_test.py` | Diario, caixa, produtos, fiados, estoque, comandas e validacoes |

Matriz detalhada: [Testes por Modulo](../matrix/tests-by-module.md).

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

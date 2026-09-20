# Testes

## Ferramentas

- Pytest
- FastAPI TestClient
- SQLite em memória nos testes locais
- Fixtures `test_engine`, `test_session` e `test_container`

## Padrão de arquivos

Os testes ficam em `app/tests/`, com sufixo `_test.py`, espelhando a camada de produção que
cobrem: testes de módulo de negócio (via API, fluxo completo) ficam em
`app/tests/core/application/use_cases/`, um arquivo por módulo. Testes de composição raiz da
aplicação (criação do app, schema, endpoint de saúde) ficam direto em `app/tests/`, fora de
qualquer pasta de camada, já que não pertencem a uma camada específica.

## Cobertura por modulo

| Modulo | Arquivo principal | Cobertura |
|---|---|---|
| Health | `tests/health_test.py` | Endpoint de saude |
| Bootstrap / Infra | `tests/bootstrap_test.py` | Criacao da app, schema e container |
| Produtos e Categorias | `tests/core/application/use_cases/produtos_categorias_test.py` | Ciclo de vida, filtros e validacoes |
| Estoque | `tests/core/application/use_cases/estoque_test.py` | Consultas, entrada, ajuste e historico |
| Comandas e Itens | `tests/core/application/use_cases/comandas_test.py` | Criacao, itens, estoque e cancelamento |
| Pagamentos e Fechamento | `tests/core/application/use_cases/pagamentos_test.py` | Fechamento, pagamentos e regressao de status |
| Caixa Diario | `tests/core/application/use_cases/caixa_test.py` | Abertura, movimentacoes, pagamentos e fechamento |
| Clientes | `tests/core/application/use_cases/clientes_test.py` | Cadastro, filtros, ativacao, inativacao e duplicidade |
| Fiado / Pendencias | `tests/core/application/use_cases/fiado_test.py` | Pendencias, vencidos, quitacao e cliente inativo |
| Relatorios basicos | `tests/core/application/use_cases/relatorios_test.py` | Diario, caixa, produtos vendidos, consumo de estoque, fiados, estoque, comandas e validacoes |
| Configuracoes | `tests/core/application/use_cases/configuracoes_test.py` | Configuracao padrao, update, patch, CORS e regra de estoque negativo |
| Acesso / Senha | `tests/core/application/use_cases/configuracoes_test.py` | Definicao, troca, validacao e protecao do hash |

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

# Comandos Make e Automações Locais

O `app/Makefile` concentra comandos frequentes para desenvolvedores e agentes de
código. Ele funciona tanto com `.venv` local quanto dentro do DevContainer,
usando o Python global do container quando a `.venv` não existe.

Execute os comandos dentro de `app/`.

## Descoberta

| Comando | Uso |
|---|---|
| `make help` | Lista comandos disponíveis |
| `make doctor` | Mostra versões e ferramentas detectadas |

## Ambiente

| Comando | Uso |
|---|---|
| `make install` | Cria `.venv` e instala dependências |
| `make run` | Sobe a API localmente |
| `make clean` | Remove caches, cobertura e `.venv` |

## Qualidade

| Comando | Uso |
|---|---|
| `make build` | Executa `py_compile` em `api.py` |
| `make test` | Roda testes não integração |
| `make test-verbose` | Roda testes com saída detalhada |
| `make test-coverage` | Roda testes com cobertura mínima de 90% |
| `make coverage` | Alias para `test-coverage` |
| `make format` | Aplica Black e Isort |
| `make format-check` | Verifica Black e Isort sem alterar arquivos |
| `make lint` | Executa Flake8 e Mypy |
| `make validate` | Build, formatação, lint e cobertura |
| `make check` | Validação sem formatar arquivos |
| `make ci` | Alias para `check` |
| `make ci-docker` | `check`, `compose-config` e `docker-build` |

Use `make check` quando quiser uma validação somente leitura. Use
`make validate` quando estiver confortável em deixar Black/Isort ajustarem os
arquivos.

## Docker Compose da API

| Comando | Uso |
|---|---|
| `make compose-config` | Valida `app/docker-compose.yml` |
| `make docker-build` | Constrói imagem da API |
| `make up` | Sobe API e Postgres |
| `make down` | Para e remove containers |
| `make ps` | Lista serviços |
| `make logs` | Acompanha logs |
| `make migrate` | Aplica migrations no container da API |

Por padrão, os comandos usam `POSTGRES_PASSWORD=local-dev-only`. Para sobrescrever:

```bash
POSTGRES_PASSWORD=outra-senha make compose-config
```

## DevContainer

Os comandos abaixo devem ser executados em `app/` a partir do host:

| Comando | Uso |
|---|---|
| `make dev-up` | Sobe o DevContainer |
| `make dev-ps` | Lista serviços do DevContainer |
| `make dev-validate` | Executa `make validate` dentro do DevContainer |
| `make dev-down` | Derruba o DevContainer |

## Rotina recomendada

Para uma alteração de documentação:

```bash
make check
```

Para uma alteração de código:

```bash
make validate
make compose-config
```

Antes de abrir uma PR:

```bash
make ci
```

Quando o ambiente tiver Docker CLI disponível e a mudança envolver Docker ou
Compose:

```bash
make ci-docker
```

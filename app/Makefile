.PHONY: help install doctor build test it test-integration test-verbose test-coverage coverage format format-check lint validate check ci ci-docker clean docker-build compose-config up down logs ps migrate dev-up dev-down dev-ps dev-validate

IMAGE_NAME=area-verde-api
CONTAINER_NAME=area-verde-api-service
VENV ?= .venv
PYTHON ?= $(shell if [ -x "$(VENV)/bin/python" ]; then echo "$(VENV)/bin/python"; elif command -v python >/dev/null 2>&1; then echo python; else echo python3; fi)
PIP ?= $(shell if [ -x "$(VENV)/bin/pip" ]; then echo "$(VENV)/bin/pip"; elif command -v pip >/dev/null 2>&1; then echo pip; else echo pip3; fi)
POSTGRES_PASSWORD ?= local-dev-only
COVERAGE_TARGETS ?= --cov=adapter --cov=api --cov=core --cov=infra

help:
	@echo "Area Verde API - comandos disponíveis"
	@echo ""
	@echo "Ambiente:"
	@echo "  make install          Cria .venv e instala dependências"
	@echo "  make doctor           Mostra ferramentas e versões detectadas"
	@echo "  make run              Sobe a API localmente"
	@echo ""
	@echo "Qualidade:"
	@echo "  make build            Compila api.py"
	@echo "  make test             Executa testes não integração"
	@echo "  make test-coverage    Executa testes com cobertura mínima"
	@echo "  make format           Aplica black e isort"
	@echo "  make format-check     Verifica black e isort sem alterar arquivos"
	@echo "  make lint             Executa flake8 e mypy"
	@echo "  make validate         Build, format, lint e cobertura"
	@echo "  make check            Build, format-check, lint e cobertura"
	@echo "  make ci               Alias para check"
	@echo "  make ci-docker        Check + docker compose config + docker build"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Constrói a imagem da API"
	@echo "  make compose-config   Valida docker-compose.yml"
	@echo "  make up/down/logs/ps  Opera o compose da API"
	@echo "  make migrate          Aplica migrations no container da API"
	@echo ""
	@echo "DevContainer:"
	@echo "  make dev-up           Sobe o DevContainer"
	@echo "  make dev-validate     Roda make validate dentro do DevContainer"
	@echo "  make dev-down         Derruba o DevContainer"

install:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

doctor:
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Python path: $$(command -v $(PYTHON) || true)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "Make: $$(make --version | head -n 1)"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'not available')"
	@echo "Docker Compose: $$(docker compose version 2>/dev/null || echo 'not available')"

build:
	$(PYTHON) -m py_compile api.py

test:
	$(PYTHON) -m pytest . -v -m "not integration"

it:
	$(PYTHON) -m pytest . -v -m "integration"

test-integration:
	$(PYTHON) -m pytest . -v -m "integration"

test-verbose:
	$(PYTHON) -m pytest . -v -s -m "not integration"

test-coverage:
	$(PYTHON) -m pytest . $(COVERAGE_TARGETS) --cov-report=term-missing --cov-report=html --cov-fail-under=90 --cov-config=.coveragerc -m "not integration"

coverage: test-coverage

format:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .

format-check:
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .

lint:
	$(PYTHON) -m flake8 --max-line-length=88 --exclude=.venv .
	$(PYTHON) -m mypy --ignore-missing-imports --explicit-package-bases .

validate: build format lint test-coverage
	@echo "Full validation complete"

check: build format-check lint test-coverage
	@echo "Read-only validation complete"

ci: check
	@echo "CI validation complete"

ci-docker: check compose-config docker-build
	@echo "CI-like validation complete"

run:
	PYTHONPATH=$$PYTHONPATH:. $(PYTHON) api.py

docker-build:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) docker compose build

compose-config:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) docker compose config

up:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) docker compose up -d

down:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) docker compose down

migrate:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) docker compose exec api alembic upgrade head

logs:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) docker compose logs -f

ps:
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) docker compose ps

dev-up:
	docker compose -f ../.devcontainer/docker-compose.yml up -d

dev-down:
	docker compose -f ../.devcontainer/docker-compose.yml down

dev-ps:
	docker compose -f ../.devcontainer/docker-compose.yml ps

dev-validate:
	docker compose -f ../.devcontainer/docker-compose.yml exec -T devcontainer bash -lc 'cd /workspaces/area-verde/app && make validate'

clean:
	rm -rf $(VENV)
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

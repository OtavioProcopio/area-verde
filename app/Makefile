.PHONY: install build test test-verbose test-coverage format lint validate clean docker-build up down logs ps migrate

IMAGE_NAME=area-verde-api
CONTAINER_NAME=area-verde-api-service

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

build:
	. .venv/bin/activate && python -m py_compile api.py

test:
	. .venv/bin/activate && python -m pytest . -v -m "not integration"

it:
	. .venv/bin/activate && python -m pytest . -v -m "integration"

test-integration:
	. .venv/bin/activate && python -m pytest . -v -m "integration"

test-verbose:
	. .venv/bin/activate && python -m pytest . -v -s -m "not integration"

test-coverage:
	. .venv/bin/activate && python -m pytest . --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=90 --cov-config=.coveragerc -m "not integration"

format:
	. .venv/bin/activate && black .
	. .venv/bin/activate && isort .

lint:
	. .venv/bin/activate && flake8 --max-line-length=88 --exclude=.venv .
	. .venv/bin/activate && mypy --ignore-missing-imports --explicit-package-bases .

validate: build format lint test-coverage
	@echo "Full validation complete"

run:
	. .venv/bin/activate && export PYTHONPATH=$$PYTHONPATH:. && python api.py

docker-build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

migrate:
	docker compose exec api alembic upgrade head

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	rm -rf .venv
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

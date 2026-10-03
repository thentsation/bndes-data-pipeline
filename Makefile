.PHONY: install run test coverage lint format typecheck docker-build docker-run clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r config/requirements.txt
	$(PIP) install -r config/requirements-dev.txt

run:
	LOCAL_OUTPUT_DIR=./data $(PYTHON) -c "from src.app import lambda_handler; print(lambda_handler({'year': 2023}, None))"

test:
	$(PYTHON) -m pytest

coverage:
	$(PYTHON) -m pytest --cov=src --cov-report=term-missing

lint:
	$(VENV)/bin/ruff check .

format:
	$(VENV)/bin/ruff format .

typecheck:
	$(VENV)/bin/mypy

docker-build:
	docker build --target runtime -f docker/Dockerfile -t bndes-lambda .

docker-run: docker-build
	docker run --rm -p 9000:8080 \
		-e LOCAL_OUTPUT_DIR=/tmp/local_data \
		-v $$(pwd)/data:/tmp/local_data \
		bndes-lambda

clean:
	find . -type d -name __pycache__ -not -path './$(VENV)/*' -exec rm -rf {} +
	find . -type d -name .pytest_cache -not -path './$(VENV)/*' -exec rm -rf {} +
	find . -type f -name '*.pyc' -not -path './$(VENV)/*' -delete
	rm -f .coverage

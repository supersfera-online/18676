.PHONY: install lint format test cov check security shell clean

install:
	pip install -e ".[dev]"
	pre-commit install

format:
	ruff format src tests
	ruff check --fix src tests

lint:
	ruff check src tests
	ruff format --check src tests
	mypy

test:
	pytest

cov:
	pytest --cov --cov-report=term-missing

security:
	bandit -c pyproject.toml -r src

shell:
	shellcheck scripts/*.sh

check: lint test security shell

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

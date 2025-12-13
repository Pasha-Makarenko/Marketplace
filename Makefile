.PHONY: help ruff ruff-fix format mypy test check

UV := uv run

help:
	@echo "Available targets:"
	@echo "  ruff       - run ruff lint"
	@echo "  ruff-fix   - run ruff lint with autofix"
	@echo "  format     - format code with ruff"
	@echo "  mypy       - type-check src/ with mypy"
	@echo "  test       - run pytest"
	@echo "  check      - format check + lint + mypy + pytest"

ruff:
	$(UV) ruff check .

ruff-fix:
	$(UV) ruff check --fix .

format:
	$(UV) ruff format .

mypy:
	$(UV) mypy src

test:
	$(UV) pytest

check: format ruff mypy test

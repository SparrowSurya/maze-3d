.PHONY: run lint format typecheck check fix help

# Default target
all: lint typecheck

run:
	uv run main.py

lint:
	uv run ruff check way/ main.py

format:
	uv run ruff format way/ main.py

typecheck:
	uv run pyright way/ main.py

# Run both lint and typecheck
check: lint typecheck

# Fix linting issues and format code
fix:
	uv run ruff check --fix way/ main.py
	uv run ruff format way/ main.py

help:
	@echo "Available targets:"
	@echo "  run       - Run the game"
	@echo "  lint      - Run ruff linter"
	@echo "  format    - Run ruff formatter"
	@echo "  typecheck - Run pyright type checker"
	@echo "  check     - Run both lint and typecheck"
	@echo "  fix       - Run ruff fix and format"
	@echo "  help      - Show this help message"

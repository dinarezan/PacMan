SRC = src
VENV = .venv
MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs
EXCLUDES = --exclude '^$(VENV)/'


install:
	uv sync

run:
	uv run python -m $(SRC)

debug:
	uv run python -m pdb -m $(SRC)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)
	rm -rf uv.lock

lint:
	uv run flake8 . --exclude $(VENV)
	uv run mypy . $(EXCLUDES) $(MYPY_FLAGS)

lint-strict:
	uv run flake8 . --exclude $(VENV)
	uv run mypy . $(EXCLUDES) --strict

.PHONY: install run debug clean fclean lint lint-strict
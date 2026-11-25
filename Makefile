SRC = src
VENV = .venv
MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs
MYPY_EXCLUDES = --exclude '^$(VENV)/'
FLAKE8_EXCLUDES = --extend-exclude $(VENV),mazegenerator.py


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
	uv run flake8 . $(FLAKE8_EXCLUDES)
	uv run mypy . $(MYPY_EXCLUDES) $(MYPY_FLAGS)

lint-strict:
	uv run flake8 . $(FLAKE8_EXCLUDES)
	uv run mypy . $(MYPY_EXCLUDES) --strict

.PHONY: install run debug clean fclean lint lint-strict
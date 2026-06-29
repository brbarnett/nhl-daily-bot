run:
	uv run main.py

fix:
	uv run ruff format .
	uv run ruff check --fix .

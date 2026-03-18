.PHONY: dev bot lint test format

dev:
	uv run uvicorn app.main:app --reload --port 8000

bot:
	uv run python -m src.bot.main

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

.PHONY: dev build up up-bot down

dev:
	cd apps/backend && uv run uvicorn src.main:app --reload --reload-dir src

build:
	docker compose up --build

up:
	docker compose up

up-bot:
	docker compose --profile bot up --build

down:
	docker compose down

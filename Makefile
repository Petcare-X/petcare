.PHONY: dev build up up-bot down

dev:
	cd apps/backend && uv run uvicorn src.main:app --reload --reload-dir src

build:
	docker compose --env-file .env.docker up --build

up:
	docker compose --env-file .env.docker up

up-bot:
	docker compose --env-file .env.docker --profile bot up --build

down:
	docker compose --env-file .env.docker down

clean:
	docker compose --env-file .env.docker down --rmi all -v
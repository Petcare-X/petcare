dev:
	cd apps/backend && uv run uvicorn src.main:app --reload --reload-dir src
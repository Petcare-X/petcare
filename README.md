# Petcare Monorepo

Fullstack монорепо: React + FastAPI, управляемый Turborepo.

## Стек

| Слой | Технологии |
|------|-----------|
| **Frontend** | React 19, TypeScript, Vite — порт 3000 |
| **Backend** | FastAPI, Python 3.12, Pydantic v2 — порт 8000 |
| **Shared** | TypeScript типы (`@monorepo/shared-types`) |
| **JS tooling** | Bun, Turborepo |
| **Python tooling** | uv, ruff, pytest |

## Структура

```
.
├── apps/
│   ├── frontend/        # React + Vite (порт 3000)
│   └── backend/         # FastAPI (порт 8000)
├── packages/
│   └── shared-types/    # Общие TypeScript типы
├── package.json         # Bun workspace + postinstall
├── turbo.json           # Turborepo конфиг
└── pyproject.toml       # uv workspace root
```

## Требования

- [Bun](https://bun.sh) >= 1.2
- [uv](https://docs.astral.sh/uv/) >= 0.5

## Установка и запуск

```bash
# Установить все зависимости (JS + Python автоматически через postinstall)
bun install

# Запустить frontend + backend одновременно
bun run dev
```

Готово. Открывайте:

| Адрес | Что там |
|-------|---------|
| http://localhost:3000 | React приложение |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |

## Другие команды

```bash
# Сборка
bun run build

# Линтинг всего монорепо
bun run lint

# Тесты Python
cd apps/backend && uv run pytest -v

# Автоисправление Python кода
cd apps/backend && uv run ruff check --fix . && uv run ruff format .
```
> Фронтенд обращается к `/api/*` — Vite проксирует запросы на `http://localhost:8000`.

# Backend

## Что нужно для запуска

- `Python 3.12`
- `uv`
- `Docker` и `docker compose`

Backend использует:

- `PostgreSQL`
- `MinIO`
- `Alembic`

Если нужен только API без фото и документов, часть ручек будет работать и без `MinIO`, но для нормального локального окружения лучше поднимать и БД, и хранилище.

## Локальный запуск backend

### 1. Поднять PostgreSQL и MinIO

Из корня репозитория:

```bash
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up -d postgres minio minio-init
```

### 2. Настроить env для локального backend

```bash
cd apps/backend
cp .env.example .env
```

Заполните `.env`. Минимально нужны:

```env
DATABASE_URL=postgresql+asyncpg://admin:secret@127.0.0.1:5432/db
JWT_SECRET_KEY=replace_with_at_least_32_characters_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

MINIO_ENDPOINT=127.0.0.1:9000
MINIO_PUBLIC_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=access_key
MINIO_SECRET_KEY=secret_key
MINIO_BUCKET_PRIVATE=bucket-private
MINIO_SECURE=false
MINIO_PUBLIC_SECURE=false
MINIO_REGION=us-east-1
MINIO_PRESIGNED_DOWNLOAD_TTL_SEC=3600

ENV=dev
INVITE_BASE_URL=http://localhost:5173
ENABLE_ADMIN_IMPORTS=true
YANDEX_GEOCODER_API_KEY=

OPENROUTER_API_KEY=
OPENROUTER_MODEL=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions

TELEGRAM_BOT_TOKEN=
TELEGRAM_BOT_INTERNAL_TOKEN=
```

### 3. Установить зависимости и применить миграции

Из `apps/backend`:

```bash
uv sync --frozen
uv run alembic upgrade head
```

### 4. Запустить backend

Из `apps/backend`:

```bash
make dev
```

После запуска:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## Запуск backend через контейнеры

### 1. Подготовить env для compose

Из корня репозитория:

```bash
cp .env.docker.example .env.docker
```

### 2. Запустить backend вместе с БД и хранилищем

Из корня репозитория:

```bash
docker compose --env-file .env.docker up --build backend
```

Compose сам поднимет зависимости:

- `postgres`
- `minio`
- `minio-init`
- `backend`

При старте `backend` контейнер автоматически:

1. синхронизирует зависимости
2. запускает `alembic upgrade head`
3. поднимает `uvicorn`

Полный dev-стек можно поднять так:

```bash
make build
```

После запуска:

- backend: `http://localhost:8000`
- MinIO API: `http://localhost:9000`
- MinIO console: `http://localhost:9001`

Остановить сервисы:

```bash
make down
```

Если нужно удалить и volumes:

```bash
make clean
```

## Загрузка CSV через `upload_data`

Эти эндпоинты нужны для импорта данных карты:

- ветклиники
- dog-friendly места
- груминг-салоны

Роуты подключаются только если выставлен `ENABLE_ADMIN_IMPORTS=true`. Файл должен быть в `UTF-8` или `UTF-8 with BOM`.

### Эндпоинты

- `POST /admin/upload-data/import-vet-csv`
- `POST /admin/upload-data/import-dogplace-csv`
- `POST /admin/upload-data/import-salons-csv`

### Формат запроса

Во всех случаях отправляется `multipart/form-data` с полем `file`.

Примеры:

```bash
curl -X POST http://localhost:8000/admin/upload-data/import-vet-csv \
  -F "file=@/absolute/path/to/vets.csv"
```

```bash
curl -X POST http://localhost:8000/admin/upload-data/import-dogplace-csv \
  -F "file=@/absolute/path/to/dogplaces.csv"
```

```bash
curl -X POST http://localhost:8000/admin/upload-data/import-salons-csv \
  -F "file=@/absolute/path/to/salons.csv"
```

### Ответ сервера

Импорт возвращает сводку по файлу:

```json
{
  "total_rows": 10,
  "imported_rows": 8,
  "skipped_rows": 2,
  "errors": [
    {
      "row_number": 4,
      "error": "Vet clinic already exists: Example",
      "raw_data": {
        "vet_name": "Example"
      }
    }
  ]
}
```

## Загрузка CSV через скрипты

### Когда использовать

Скрипты в `src/import/scripts` нужны для загрузки справочников в БД:

- типов животных
- пород
- типов документов

Скрипты подключаются напрямую к БД через `DATABASE_URL`, поэтому перед запуском должны быть:

- доступна БД
- применены миграции
- заполнен `apps/backend/.env` или корректно переданы переменные окружения

### Локальный запуск скриптов

Из `apps/backend`:

для типов животных:
```bash
uv run python src/import/scripts/import_animals_types.py src/import/csv_files/animal_types.csv
```

для пород животных:
```bash
uv run python src/import/scripts/import_animals_breeds.py src/import/csv_files/animal_breeds.csv
```

для типов документов:
```bash
uv run python src/import/scripts/import_document_types.py src/import/csv_files/document_types.csv
```

### Запуск скриптов внутри контейнера backend

Если backend уже поднят через compose:
```bash
cd apps/backend
```

для типов животных:
```bash
docker compose --env-file .env exec backend \
  uv run python src/import/scripts/import_animals_types.py src/import/csv_files/animal_types.csv
```

для пород животных:
```bash
docker compose --env-file .env exec backend \
  uv run python src/import/scripts/import_animals_breeds.py src/import/csv_files/animal_breeds.csv
```

для типов документов:
```bash
docker compose --env-file .env exec backend \
  uv run python src/import/scripts/import_document_types.py src/import/csv_files/document_types.csv
```

Готовые таблицы уже лежат в:

- `src/import/csv_files/animal_types.csv`
- `src/import/csv_files/animal_breeds.csv`
- `src/import/csv_files/document_types.csv`

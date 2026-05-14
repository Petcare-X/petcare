# Backend

## Что нужно для запуска

- `Python 3.12`
- `uv`
- `Docker` и `docker compose`

Backend использует:

- `PostgreSQL` как основную БД
- `MinIO` как объектное хранилище для фото и документов
- `Alembic` для миграций

Если нужен только API без фото и документов, часть ручек будет работать и без `MinIO`, но для нормального локального окружения лучше поднимать и БД, и хранилище.

## Локальный запуск backend

### 1. Поднять PostgreSQL и MinIO

Самый простой вариант для локальной разработки: запустить только инфраструктуру через `docker compose`, а сам backend держать как обычный процесс.

Из корня репозитория:

```bash
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up -d postgres minio minio-init
```

Что поднимется:

- `postgres` на порту из `POSTGRES_PORT`
- `minio` на `http://localhost:9000`
- `minio console` на `http://localhost:9001`
- `minio-init` автоматически создаст бакет `MINIO_BUCKET_PRIVATE`

Если вы хотите использовать не контейнеры, а локально установленный `PostgreSQL` и отдельный `MinIO`, это тоже возможно. Тогда просто укажите реальные хосты и порты в `apps/backend/.env`.

### 2. Настроить env для локального backend

Локальный backend читает переменные из файла `apps/backend/.env`.

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
MINIO_ACCESS_KEY=access_key
MINIO_SECRET_KEY=secret_key
MINIO_BUCKET_PRIVATE=bucket-private
MINIO_SECURE=false
MINIO_REGION=us-east-1

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

Важно:

- в `DATABASE_URL` для локального процесса нужен хост `127.0.0.1`, а не `postgres`
- если в `.env.docker` вы изменили `POSTGRES_PORT`, тот же порт нужно указать и в локальном `DATABASE_URL`
- в `MINIO_ENDPOINT` для локального процесса нужен `127.0.0.1:9000`, а не `minio:9000`
- `ENABLE_ADMIN_IMPORTS=true` нужно, если хотите использовать admin-эндпоинты для импорта CSV
- `YANDEX_GEOCODER_API_KEY` нужен для `upload_data`, потому что импорт мест делает геокодирование адресов

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

или напрямую:

```bash
uv run uvicorn src.main:app --reload --port 8000
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

Проверьте `.env.docker`. Для контейнерного режима важно, что backend внутри сети compose ходит:

- в БД по хосту `postgres`
- в MinIO по хосту `minio:9000`

Поэтому в `DATABASE_URL` и `MINIO_ENDPOINT` должны остаться именно эти значения, а не `127.0.0.1`.

Для стандартного локального `docker-compose.yml` также должен быть:

```env
MINIO_SECURE=false
```

Потому что MinIO в этом сценарии поднимается без TLS и доступен по обычному `http`.

Если нужны CSV-импорты через admin-ручки, добавьте в `.env.docker`:

```env
ENABLE_ADMIN_IMPORTS=true
YANDEX_GEOCODER_API_KEY=your_key
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
docker compose --env-file .env.docker up --build
```

После запуска:

- backend: `http://localhost:8000`
- MinIO API: `http://localhost:9000`
- MinIO console: `http://localhost:9001`

Остановить сервисы:

```bash
docker compose --env-file .env.docker down
```

Если нужно удалить и volumes:

```bash
docker compose --env-file .env.docker down -v
```

## Загрузка CSV через `upload_data`

### Когда использовать

Эти эндпоинты нужны для импорта данных карты:

- ветклиники
- dog-friendly места
- груминг-салоны

Роуты подключаются только если выставлен `ENABLE_ADMIN_IMPORTS=true`.

Важно:

- ручки скрыты из OpenAPI, потому что объявлены с `include_in_schema=False`
- они всё равно доступны по прямому URL
- для каждого адреса вызывается геокодер, поэтому нужен `YANDEX_GEOCODER_API_KEY`
- файл должен быть в `UTF-8` или `UTF-8 with BOM`

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

### Обязательные колонки CSV

Для ветклиник:

```text
vet_name
vet_city
vet_street
vet_building_number
vet_working_hours
vet_is_24_7
vet_status
vet_phone
```

Для dog-friendly мест:

```text
dogfriendly_place_name
dogfriendly_place_city
dogfriendly_place_street
dogfriendly_place_building_number
dogfriendly_place_working_hours
dogfriendly_place_status
```

Для салонов:

```text
salon_name
salon_city
salon_street
salon_building_number
salon_phone
salon_website
salon_working_hours
salon_status
```

Полезные детали по данным:

- `vet_is_24_7` понимает значения `true/false`, `1/0`, `yes/no`, `y/n`, `да/нет`
- если строка невалидна или дублирует существующую запись, она попадёт в список ошибок и будет пропущена
- импорт не обновляет существующие записи, а только создаёт новые

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

```bash
uv run python src/import/scripts/import_animals_types.py src/import/csv_files/animal_types.csv
```

```bash
uv run python src/import/scripts/import_animals_breeds.py src/import/csv_files/animal_breeds.csv
```

```bash
uv run python src/import/scripts/import_document_types.py src/import/csv_files/document_types.csv
```

### Запуск скриптов внутри контейнера backend

Если backend уже поднят через compose:

```bash
docker compose --env-file .env.docker exec backend \
  uv run python src/import/scripts/import_animals_types.py src/import/csv_files/animal_types.csv
```

```bash
docker compose --env-file .env.docker exec backend \
  uv run python src/import/scripts/import_animals_breeds.py src/import/csv_files/animal_breeds.csv
```

```bash
docker compose --env-file .env.docker exec backend \
  uv run python src/import/scripts/import_document_types.py src/import/csv_files/document_types.csv
```

### Формат CSV для скриптов

`import_animals_types.py`:

```text
animal_name
```

`import_animals_breeds.py`:

```text
animal_type_id
animal_breed
```

`import_document_types.py`:

```text
document_name
```

Готовые примеры уже лежат в:

- `src/import/csv_files/animal_types.csv`
- `src/import/csv_files/animal_breeds.csv`
- `src/import/csv_files/document_types.csv`

Поведение скриптов:

- дубликаты не перезаписываются, а пропускаются
- пустые строки пропускаются
- результат выводится в stdout в формате `Created / skipped`

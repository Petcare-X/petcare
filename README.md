# Petcare-X

## Установка PostgreSQL

Ubuntu/Debian:

```bash
sudo apt install postgresql
sudo systemctl start postgresql
```

Если есть Homebrew:

```bash
brew install postgresql@16
brew services start postgresql@16
```

## Настройка базы данных

```bash
psql postgres
```

```sql
CREATE USER "petcare-admin" WITH PASSWORD 'kQrA3-oBVn';
CREATE DATABASE petcare OWNER "petcare-admin";
\q
```

## Установка

```bash
uv sync
cp apps/backend/.env.example apps/backend/.env
```

## Миграции

```bash
cd apps/backend
uv run alembic upgrade head
```

## Запуск

```bash
make dev
```

Сервер: http://localhost:8000

## API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /users | Создать пользователя |
| GET | /users | Список пользователей |
| GET | /users/{id} | Получить пользователя |
| PATCH | /users/{id}/data | Обновить данные |
| PATCH | /users/{id}/contacts | Обновить контакты |
| DELETE | /users/{id} | Удалить пользователя |
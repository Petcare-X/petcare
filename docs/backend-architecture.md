# Backend Architecture: PetCare

## 1. Назначение backend
Backend проекта `PetCare` реализован как асинхронный API-сервис на `FastAPI`, который обслуживает:
- аутентификацию и управление сессиями пользователей;
- управление пользователями и профилями питомцев;
- загрузку и выдачу фото и документов питомцев через object storage;
- совместный доступ к карточкам питомцев через инвайты;
- выдачу картографических точек для ветклиник и dog-friendly мест;
- чат с ИИ-помощником через внешнюю LLM-интеграцию;
- импорт справочных данных по клиникам и dog-friendly местам из CSV.

Документ описывает текущее состояние backend на основе кода в `apps/backend/src`.

## 2. Текущий стек
- Язык: `Python 3.12+`
- Web framework: `FastAPI`
- ASGI server: `uvicorn`
- ORM: `SQLAlchemy 2.x` (`asyncio`)
- База данных: `PostgreSQL` (`asyncpg`)
- Миграции: `Alembic`
- Валидация: `Pydantic v2`
- Object storage: `MinIO` (`aioboto3`)
- HTTP-клиент для интеграций: `httpx`
- Telegram bot/integration: `aiogram`
- LLM provider: `OpenRouter`

Ключевые зависимости описаны в [pyproject.toml].

## 3. Структура backend
Текущая структура приложения:

```text
apps/backend/src/
  api/            HTTP-роуты и FastAPI endpoints
  service/        бизнес-логика и интеграции
  models/         SQLAlchemy ORM-модели
  schemas/        Pydantic-схемы request/response
  core/           конфигурация, БД, security
  bot/            Telegram bot flows
  third_party/    локальные обертки внешних интеграций
  exceptions.py   единая ошибка приложения и exception handlers
  main.py         точка входа FastAPI
```

Архитектурный стиль в текущем коде:
- `api` слой принимает HTTP-запросы, прокидывает зависимости и вызывает сервисы;
- `service` слой инкапсулирует бизнес-логику и операции над ORM/интеграциями;
- `models` описывают структуру persistence;
- `schemas` формируют публичный контракт API;
- `core` содержит cross-cutting concerns: конфиг, security, database session.

Это близко к layered architecture без строгого выделения repository layer.

## 4. Точка входа и композиция приложения
Главная точка входа находится в `apps/backend/src/main.py`:
- создается экземпляр `FastAPI`;
- регистрируются глобальные обработчики исключений;
- подключается общий `api_router`.

Сборка маршрутов выполняется в `apps/backend/src/api/router.py`. Сейчас backend агрегирует следующие bounded contexts:
- `users`
- `pets`
- `document-types` и вложенные `pet documents`
- `invites` / `pet sharing`
- `auth`
- `upload-data`
- `map-points`
- `llm-chat`

## 5. Конфигурация и окружение
Конфигурация задается через `pydantic-settings` в `apps/backend/src/core/config.py`.

Основные переменные:
- `DATABASE_URL`
- `INVITE_BASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_INTERNAL_TOKEN`
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET_PRIVATE`
- `MINIO_SECURE`
- `MINIO_REGION`
- `MINIO_PRESIGNED_UPLOAD_TTL_SEC`
- `MINIO_PRESIGNED_DOWNLOAD_TTL_SEC`
- `YANDEX_GEOCODER_API_KEY`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`

Особенности:
- `.env` читается напрямую через `BaseSettings`;
- часть интеграций является опциональной, но отдельные флоу падают при отсутствии нужных переменных;
- `StorageService` явно проверяет обязательность MinIO-конфига перед работой.

## 6. Работа с базой данных
Слой БД находится в `apps/backend/src/core/db.py`.

Текущая реализация:
- используется `DeclarativeBase`;
- `create_async_engine` и `async_sessionmaker`;
- сессия прокидывается через dependency `get_db()`;
- `expire_on_commit=False`, что упрощает работу с ORM-объектами после `commit`.

Миграции:
- миграции хранятся в `apps/backend/alembic/versions`;
- схема активно эволюционировала: auth, documents, map data, LLM tables, sharing.

## 7. Доменные контексты и сущности

### 7.1 Users / Authentication
Ключевые сущности:
- `UserInfo`
- `RefreshToken`

`UserInfo` хранит:
- имя;
- email;
- номер телефона;
- дату рождения;
- ссылку/ключ фото, которое может отсутствовать.

`RefreshToken` хранит:
- `user_id`;
- `token_jti`;
- `expires_at`;
- `revoked`;
- опционально `user_agent` и `ip_address` на уровне модели, но в текущей логике они не используются.

`AuthIdentities` хранит:
- `user_id`;
- `provider` (телеграм или почта);
- email и хэш пароля (если регистрация произошла через почту);
- телеграм (если регистрация произошла через телеграм).

Наблюдения:
- refresh tokens не являются полностью stateless: они дополнительно сохраняются в БД и могут быть отозваны.

### 7.2 Pets
Ключевая сущность:
- `PetInfo`

Сущность питомца хранит:
- владельца (`user_id`);
- имя;
- дату рождения;
- тип животного;
- пол животного;
- породу;
- pedigree flag;
- набор размерных параметров;
- вес;
- флаг стерилизации;
- особенности животного в формате текста (опционально);
- metadata фото (`object_key`, `content_type`, `size_bytes`, `etag`, `uploaded_at`).

Справочники:
- `AnimalType`
- `AnimalBreed`

Особенности домена:
- фото питомца хранится как внешний файл в object storage, а БД держит метаданные;
- фото питомца является необязательной частью профиля и может отсутствовать при создании карточки;
- породы животных должны быть привязаны к конкретному типу животного;
- frontend и bot flows должны получать породы через фильтрацию по выбранному типу;
- shared access вычисляется отдельно через таблицу `SharedUser`;
- при выдаче response backend возвращает `is_shared` как derived field.

### 7.3 Documents
Ключевые сущности:
- `PetDocument`
- `DocumentType`

`PetDocument` хранит:
- привязку к питомцу;
- тип документа;
- `custom_name`;
- `object_key` в storage;
- метаданные загруженного файла.

Особенности:
- физический файл живет в object storage;
- объектный ключ формируется детерминированно на основе пользователя, питомца и типа документа;
- изменение типа уже загруженного документа запрещено на уровне сервиса.

### 7.4 Sharing
Ключевые сущности:
- `PetInvite`
- `SharedUser`

`PetInvite` описывает одноразовое или многоразовое приглашение:
- `invite_code`;
- `max_uses`;
- `uses_count`;
- `expires_at`;
- `is_active`.

`SharedUser` описывает активный или истекший доступ:
- кому расшарено;
- к какому питомцу;
- начало доступа;
- окончание доступа.

Особенности:
- право делиться доступом есть только у владельца питомца;
- пользователь не может принять приглашение в собственный pet profile;
- инвайт может автоматически деактивироваться при превышении `max_uses`.

### 7.5 Map / Places
Ключевые сущности:
- `VetClinic`
- `DogFriendlyPlace`
- `GroomingSalons`
- `SuitableVetClinic`
- `SuitableDogFriendlyPlace`

Текущее API карты отдает:
- только активные точки;
- упрощенный response для карты;
- человекочитаемый признак `24/7`.

Важно:
- модели `SuitableVetClinic` и `SuitableDogFriendlyPlace` уже есть в домене, но текущий публичный API карты не использует их для персонализации выдачи.

### 7.6 LLM Chat
Ключевые сущности:
- `LlmChat`
- `LlmMessage`

Модель чата:
- принадлежит пользователю и его конкретному питомцу;
- имеет заголовок;
- может содержать custom instructions.

Модель сообщения:
- принадлежит чату;
- хранит роль (`user`, `assistant`, потенциально `system`);
- имеет данные о предыдущем сообщении (сообщении-родителе);
- хранит текст и время создания;
- хранит сообщение об ошибке (например, генерации сообщения ассистентом).

Особенности:
- чат pet-centric;
- история сообщений сохраняется в БД.

### 7.7 Import / Geo data
Справочные данные импортируются через CSV-файлы:
- ветклиники;
- dog-friendly места.

Импорт включает:
- валидацию строк через Pydantic-схемы;
- попытку геокодирования адреса;
- проверку на дубликаты;
- сохранение частично успешного результата с отчетом по ошибкам.

## 8. API-слой
API-слой расположен в `src/api/` и организован по доменным модулям.

Текущие принципы:
- маршруты обычно тонкие и не содержат бизнес-логики;
- авторизация реализована через `Depends(get_current_user)` или `Depends(get_current_user_id)`;
- вложенные роуты для документов, фото и sharing подключаются под `/pets/{pet_id}`.

Основные публичные группы маршрутов:
- `/users`
- `/auth`
- `/pets`
- `/pets/{pet_id}/photo/*`
- `/pets/{pet_id}/documents/*`
- `/pets/{pet_id}/shared-users`
- `/pets/{pet_id}/access/{user_id}`
- `/invites`
- `/map-points/*`
- `/llm-chat`

Наблюдение:
- часть внутренних и legacy-роутов отмечена через `include_in_schema=False` или `deprecated=True`.

Административные маршруты:
- `/upload-data/*`

Для них требуется отдельная административная защита, так как работа с CSV и картографическими данными должна быть доступна только администраторам.

## 9. Сервисный слой
Сервисный слой содержит основную бизнес-логику.

Ключевые сервисы:
- `AuthService`
- `UsersService` [ДОПУЩЕНИЕ: существует как доменный сервис, используется API-слоем]
- `PetsService`
- `PetPhotoService`
- `PetDocumentsService`
- `PetDocumentFilesService`
- `SharingService`
- `MapService`
- `LLMChatService`
- `OpenRouterService`
- `ImportService`
- `StorageService`

Роль сервисов:
- проверка прав доступа;
- orchestration между БД и внешними системами;
- генерация derived responses;
- компенсационные действия при частичном фейле.

Важная особенность реализации:
- в коде активно используется application service pattern;
- часть сервисов использует repository abstraction (питомцы, пользователи, шеринг, чаты и сообщения), некоторые сервисы работают с `AsyncSession` напрямую;
- некоторые сервисы инстанцируют другие сервисы внутри себя, что упрощает композицию, но ослабляет dependency injection.

## 10. Аутентификация и авторизация

### 10.1 Текущая auth-схема
Auth реализован в `apps/backend/src/core/security.py` и `apps/backend/src/api/auth.py`.

Используется:
- `HTTPBearer` для access token;
- JWT access token;
- JWT refresh token;
- persisted refresh token store в БД.

Поток login:
1. Пользователь отправляет email/password.
2. `AuthService` находит пользователя по email.
3. Проверяет `auth_provider == "email"`.
4. Проверяет пароль.
5. Создает access token.
6. Создает refresh token и сохраняет `jti` в таблицу `refresh_tokens`.

Поток refresh:
1. Удаляются истекшие refresh tokens.
2. Декодируется refresh token.
3. Проверяется тип, `sub`, `jti`.
4. Находится строка токена в БД.
5. Проверяются `revoked`, принадлежность user и срок действия.
6. Старый refresh token помечается как revoked.
7. Выпускается новая пара токенов.

Потоки Telegram auth:
- `POST /auth/telegram` проверяет `hash` Telegram Login Widget;
- `POST /auth/telegram/bot` защищен внутренним заголовком `X-Telegram-Bot-Token` и используется для bot-driven auth.

Зафиксированное продуктовое решение:
- `email/password` и Telegram являются целевыми способами входа в приложение;
- Telegram остается отдельным каналом взаимодействия и одновременно альтернативным способом авторизации.

### 10.2 Password hashing
Пароли хешируются через `pbkdf2_hmac("sha256", iterations=200_000)` с солью.

Важно:
- в коде не используется `argon2`, несмотря на наличие зависимости;
- хеширование реализовано вручную.

### 10.3 Авторизация по ролям
Формальной role model в коде нет, но фактически есть следующие уровни доступа:
- неавторизованный пользователь;
- аутентифицированный пользователь;
- владелец питомца;
- shared user с активным доступом.

Правила:
- только владелец может редактировать или удалять питомца;
- shared user может читать питомца и связанные документы, если `allow_shared=True`;
- только владелец может управлять photo/document upload и sharing;
- LLM-чаты доступны только их владельцу.

Продуктовая цель на следующую итерацию:
- shared user должен получить почти все пользовательские сценарии по питомцу, кроме редактирования данных питомца и управления шарингом;
- shared user должен иметь доступ к документам питомца.

## 11. Работа с файлами и object storage
Файловый контур строится вокруг `StorageService`, `PetPhotoService` и `PetDocumentFilesService`.

### 11.1 Общий подход
Backend не проксирует пользовательские файлы через себя в основном потоке загрузки. Вместо этого:
1. backend выдает presigned upload URL;
2. клиент загружает файл напрямую в MinIO/S3;
3. backend подтверждает загрузку и сохраняет метаданные в БД.

### 11.2 Структура object keys
Фото питомца:
- `users/{user_id}/pets/{pet_id}/photo/{uuid}.{ext}`

Документы питомца:
- `users/{user_id}/pets/{pet_id}/documents/{document_type_id}/{custom_name}.{ext}`

### 11.3 Проверки консистентности
Backend валидирует, что:
- `object_key` действительно принадлежит конкретному пользователю/питомцу/типу документа;
- объект физически существует в storage (`head_object`);
- метаданные файла считываются из storage перед сохранением в БД.

### 11.4 Компенсационные сценарии
В текущем коде есть попытки поддерживать согласованность между БД и storage:
- при неуспехе сохранения метаданных backend пытается удалить уже загруженный объект;
- при замене фото сначала сохраняется новая версия, затем удаляется старая;
- при неудаче удаления старого объекта выполняется rollback на предыдущую версию;
- при удалении документа или фото backend старается откатить состояние БД, если удаление из storage не удалось.

Это сильная сторона текущей реализации.

## 12. LLM-интеграция
Интеграция с LLM вынесена в `OpenRouterService`.

Текущий поток:
1. Пользователь создает чат.
2. При отправке нового сообщения backend загружает историю чата.
3. Формирует массив сообщений для OpenRouter.
4. Выполняет HTTP-запрос к `https://openrouter.ai/api/v1/chat/completions`.
5. Сохраняет в БД сообщение пользователя и ответ ассистента.

Ограничения текущей реализации:
- нет streaming-ответов;
- нет retry policy;
- нет rate limiting.

Зафиксированное продуктовое направление:
- данные профиля питомца должны подключаться как контекст только по явному выбору пользователя.

## 13. Карта и импорт данных

### 13.1 Map API
`MapService` возвращает только активные точки:
- ветклиники со статусом `active`;
- dog-friendly места со статусом `active`.

Текущий API карты:
- не использует геопоиск по радиусу;
- не применяет персонализацию через `Suitable*` таблицы.

Зафиксированное продуктовое направление:
- в MVP карта должна поддерживать каталог точек, фильтры и использование геоданных для определения города пользователя;
- использование точного местоположения пользователя пока не требуется.

### 13.2 ImportService
`ImportService` позволяет загружать CSV и:
- валидировать строки;
- геокодировать адреса;
- проверять уникальность;
- возвращать агрегированный отчет `imported/skipped/errors`.

Особенности:
- импорт допускает частичный успех;
- геокодирование не блокирует весь импорт, если отдельная строка не геокодируется;
- API upload-data должен быть полностью защищен и доступен только администраторам.

## 14. Обработка ошибок
Единый error model описан в `apps/backend/src/exceptions.py`.

Формат ответа:
```json
{
  "error": {
    "type": "AppErrorSubclass",
    "message": "Human-readable message",
    "status_code": 400,
    "details": {}
  }
}
```

Покрываются:
- доменные ошибки приложения;
- `HTTPException`;
- validation errors (`422`);
- любые необработанные исключения (`500`).

Плюсы:
- единый JSON формат;
- легко обрабатывать на фронтенде;
- доменные ошибки выражены именованными классами.

Риск:
- в `500` ответ может уходить `exception_message`, что удобно в dev, но рискованно для production.

## 15. Telegram bot и внутренние интеграции
В репозитории есть отдельный `src/bot/` модуль на `aiogram`.

Текущая роль бота:
- отдельный пользовательский интерфейс для части сценариев проекта;
- backend поддерживает bot-to-backend auth через `POST /auth/telegram/bot` и заголовок `X-Telegram-Bot-Token`.

На архитектурном уровне bot и HTTP API делят общую доменную модель и часть сервисов, но эксплуатируются как отдельные входные каналы.

## 16. Сильные стороны текущей архитектуры
- Четкое доменное разбиение по модулям.
- Асинхронный стек для HTTP и БД.
- Единый error contract.
- Относительно аккуратная реализация file/storage consistency.
- Persisted refresh tokens с ротацией и revoke.
- Разделение API, schemas и service layer.
- Уже заложены точки расширения для Telegram auth, sharing, LLM и карты.

## 17. Текущие ограничения и технические риски

### 17.1 Архитектурные ограничения
- Нет явного API versioning.
- Не вся работа с базой данных перенесена на repository layer.
- Зависимости сервисов в основном создаются вручную, а не через DI-контейнер.
- Нет формального разделения public/admin/internal API.

### 17.2 Security и auth
- Пароль хешируется вручную, хотя в зависимостях есть более специализированные библиотеки.
- Нет явной rate limiting защиты для auth и LLM endpoints.

### 17.3 Storage / files
- Нет явных лимитов по типу и размеру файла на уровне API-слоя.
- Нет фоновой очистки orphaned objects, если клиент не вызвал `complete`.

### 17.4 LLM
- Нет очередей задач.

### 17.5 Map / import
- CSV import требует отдельной административной авторизации, но это еще не зафиксировано в реализации.
- Геокодирование выполняется inline и может увеличивать latency импорта.
- В текущем публичном API не используется персонализация карты по питомцу.

### 17.6 Эксплуатация
- В коде не видно structured logging.
- Не описаны metrics, tracing и centralized observability.
- Тестовая стратегия в явном виде не обнаружена.

## 18. Рекомендации по следующему этапу эволюции

### Высокий приоритет
- Защитить `upload-data` маршруты административной авторизацией.
- Формализовать file limits и content-type policy.

### Средний приоритет
- Ввести structured logging и correlation/request id.
- Добавить rate limiting на auth и LLM endpoints.
- Определить стратегию хранения refresh token для web/PWA клиентов.
- Добавить cleanup job для неактуальных refresh tokens и orphaned storage objects.

### Дальнейшее развитие
- Вынести длительные внешние операции в background jobs.
- Добавить персонализированную выдачу карты через `SuitableVetClinic` и `SuitableDogFriendlyPlace`.
- При необходимости выделить admin API и internal bot API.

## 19. Полезные исходники
- `apps/backend/src/main.py`
- `apps/backend/src/api/router.py`
- `apps/backend/src/core/config.py`
- `apps/backend/src/core/db.py`
- `apps/backend/src/core/security.py`
- `apps/backend/src/exceptions.py`
- `apps/backend/src/service/pets.py`
- `apps/backend/src/service/pet_photos.py`
- `apps/backend/src/service/pet_documents.py`
- `apps/backend/src/service/pet_document_files.py`
- `apps/backend/src/service/sharing.py`
- `apps/backend/src/service/map.py`
- `apps/backend/src/service/llm_chat.py`
- `apps/backend/src/service/openrouter.py`
- `apps/backend/src/service/storage.py`

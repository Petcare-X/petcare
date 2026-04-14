# API Contract: PetCare

## 1. Назначение документа
Этот документ фиксирует текущий HTTP API-контракт проекта `PetCare` на основе backend-кода.

Он нужен для:
- frontend-разработки;
- согласования backend-изменений;
- использования ИИ-агентами как источника истины по API;
- выявления расхождений между текущей реализацией и целевой продуктовой моделью.

Связанные документы:
- продуктовые требования: `docs/PRD.md`
- frontend-архитектура: `docs/frontend-architecture.md`
- backend-архитектура: `docs/backend-architecture.md`
- матрица прав: `docs/permission-matrix.md`

## 2. Статус документа
Текущее состояние:
- документ отражает текущую backend-реализацию;
- часть продуктовых ожиданий еще не реализована на уровне API;
- такие места явно помечаются в разделе `Расхождения с целевой моделью`.

## 3. Общие правила API

### 3.1 Базовый URL
На текущем этапе маршруты используются без префикса версии, то есть без `api/v1`.

Примеры:
- `/auth/login`
- `/users/me`
- `/pets`

### 3.2 Формат данных
- request/response используют `JSON`, кроме upload сценариев с `UploadFile` в административных ручках;
- авторизация для защищенных маршрутов передается через `Authorization: Bearer <access_token>`;
- refresh token передается в теле запроса на `POST /auth/refresh`.

### 3.3 Общий формат ошибок
Сервер стремится возвращать ошибки в формате:

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

Типовые статусы:
- `400` — бизнес-ошибка, некорректный запрос;
- `401` — ошибка авторизации или токена;
- `403` — нет прав доступа;
- `404` — сущность не найдена;
- `409` — конфликт;
- `422` — ошибка валидации;
- `500` — внутренняя ошибка сервера;
- `502` — ошибка внешней интеграции, например LLM provider.

### 3.4 Общие правила авторизации
- публичные маршруты не требуют токена;
- защищенные маршруты требуют валидный access token;
- админские маршруты должны быть дополнительно защищены отдельной admin-моделью доступа.

## 4. Auth API

### 4.1 `POST /auth/login`
Назначение:
Вход пользователя по email/password.

Auth:
- не требуется

Request:
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

Response `200`:
```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer"
}
```

Ошибки:
- `401` invalid credentials
- `400` auth provider mismatch

### 4.2 `POST /auth/refresh`
Назначение:
Обновление пары access/refresh token.

Auth:
- не требуется, refresh token передается в body

Request:
```json
{
  "refresh_token": "jwt"
}
```

Response `200`:
```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer"
}
```

Ошибки:
- `401` invalid refresh token
- `404` refresh token not found

### 4.3 `POST /auth/logout`
Назначение:
Отозвать текущий refresh token.

Auth:
- не требуется в header, используется refresh token из body

Request:
```json
{
  "refresh_token": "jwt"
}
```

Response `200`:
```json
{
  "success": true
}
```

### 4.4 `POST /auth/logout-all`
Назначение:
Отозвать все refresh tokens текущего пользователя.

Auth:
- требуется bearer token

Response `200`:
```json
{
  "success": true
}
```

### 4.5 `POST /auth/telegram`
Назначение:
Авторизация через Telegram Login Widget.

Auth:
- не требуется

Request:
```json
{
  "id": 123456,
  "first_name": "Kirill",
  "last_name": "User",
  "username": "kirill",
  "photo_url": "https://example.com/avatar.jpg",
  "auth_date": 1700000000,
  "hash": "telegram_hash"
}
```

Response `200`:
```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer"
}
```

### 4.6 `POST /auth/telegram/bot`
Назначение:
Внутренний bot-driven auth.

Auth:
- внутренний заголовок `X-Telegram-Bot-Token`

Примечание:
- этот маршрут не является обычным публичным frontend-сценарием.

## 5. Users API

### 5.1 `POST /users`
Назначение:
Создание аккаунта пользователя.

Auth:
- не требуется

Request:
```json
{
  "name": "Kirill",
  "email": "user@example.com",
  "phone_number": "+79990000000",
  "password": "string",
  "birth_date": "1995-05-05"
}
```

Примечание:
- регистрация пользователя остаётся полной и требует имя, email, телефон, пароль и дату рождения;
- `photo_url` не является обязательным полем;
- если фото не загружено, `user_photo` в ответах возвращается как `null`.

Response `201`:
```json
{
  "id": 1,
  "user_name": "Kirill",
  "user_email": "user@example.com",
  "user_phone_number": "+79990000000",
  "user_date_of_birth": "1995-05-05",
  "user_photo": null,
  "telegram_id": null,
  "auth_provider": "email"
}
```

### 5.2 `GET /users/me`
Назначение:
Получение профиля текущего пользователя.

Auth:
- требуется bearer token

Response `200`:
- `UserPrivate`

### 5.3 `PATCH /users/me/data`
### 5.4 `PATCH /users/me/contacts`
Назначение:
Обновление данных пользователя.

Auth:
- требуется bearer token

Request:
- частичный `UpdateUser`

Response `200`:
- `UserPrivate`

### 5.5 `DELETE /users/me`
Назначение:
Удаление текущего пользователя.

Auth:
- требуется bearer token

Response `200`:
```json
{
  "deleted": true
}
```

## 6. Pets API

### 6.1 `POST /pets`
Назначение:
Создание питомца.

Auth:
- требуется bearer token

Request:
- `PetCreate`

Ключевые поля:
```json
{
  "pet_name": "Milo",
  "pet_date_of_birth": "2022-01-01",
  "animal_type_id": 1,
  "animal_breed_id": 2,
  "pedigree": false,
  "pet_neck_girth": 25.0,
  "pet_breast_girth": 45.0,
  "pet_length": 50.0,
  "pet_weight": 12.5,
  "pet_is_sterylyzed": true
}
```

Примечание:
- `pet_photo_object_key` не является обязательным при создании питомца;
- если фото не загружено, поля фотографии возвращаются как пустые значения (`null`);
- фото добавляется отдельным шагом через pet photo upload flow.

Response `201`:
- `PetResponse`

### 6.2 `GET /pets`
Назначение:
Список питомцев пользователя, включая расшаренных.

Auth:
- требуется bearer token

Query params:
- `offset` default `0`
- `limit` default `50`

Response `200`:
- `PetResponse[]`

### 6.3 `GET /pets/{pet_id}`
Назначение:
Получение карточки питомца.

Auth:
- требуется bearer token

Response `200`:
- `PetResponse`

Ошибки:
- `404` pet not found
- `403` access denied

### 6.4 `PATCH /pets/{pet_id}`
Назначение:
Частичное обновление питомца.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Request:
- `UpdatePet`

Response `200`:
- `PetResponse`

### 6.5 `DELETE /pets/{pet_id}`
Назначение:
Удаление питомца.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Response `200`:
```json
{
  "deleted": true
}
```

## 6A. Animal Reference API

### 6A.1 `GET /animal-types`
Назначение:
Получение списка типов животных для форм создания и редактирования питомца.

Auth:
- не требуется

Response `200`:
```json
[
  {
    "id": 1,
    "animal_name": "Собака"
  },
  {
    "id": 2,
    "animal_name": "Кошка"
  }
]
```

### 6A.2 `GET /animal-types/{animal_type_id}/breeds`
Назначение:
Получение списка пород, относящихся только к выбранному типу животного.

Auth:
- не требуется

Response `200`:
```json
[
  {
    "id": 1,
    "animal_breed": "Корги",
    "animal_type_id": 1
  }
]
```

## 7. Pet Photo API

### 7.1 `POST /pets/{pet_id}/photo/upload-url`
Назначение:
Получить presigned upload URL для фото питомца.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Request:
```json
{
  "content_type": "image/jpeg"
}
```

Response `200`:
```json
{
  "object_key": "string",
  "upload_url": "string",
  "expires_in": 900
}
```

### 7.2 `POST /pets/{pet_id}/photo/complete`
Назначение:
Подтвердить завершение загрузки фото.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Request:
```json
{
  "object_key": "string"
}
```

Response `200`:
- `PetResponse`

### 7.3 `GET /pets/{pet_id}/photo/download-url`
Назначение:
Получить временный URL для скачивания фото.

Auth:
- требуется bearer token

Access:
- владелец или shared user

Response `200`:
```json
{
  "object_key": "string",
  "download_url": "string",
  "expires_in": 300
}
```

### 7.4 `DELETE /pets/{pet_id}/photo`
Назначение:
Удалить фото питомца.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Response `200`:
```json
{
  "deleted": true
}
```

## 8. Documents API

### 8.1 `GET /document-types`
Назначение:
Получить список типов документов.

Auth:
- не требуется

Response `200`:
```json
[
  {
    "id": 1,
    "document_name": "Veterinary passport"
  }
]
```

### 8.2 `GET /pets/{pet_id}/documents`
Назначение:
Получить список документов питомца.

Auth:
- требуется bearer token

Access:
- владелец или shared user

Response `200`:
- `PetDocumentResponse[]`

### 8.3 `POST /pets/{pet_id}/documents/upload-url`
Назначение:
Получить presigned upload URL для документа.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Request:
```json
{
  "document_type_id": 1,
  "content_type": "application/pdf",
  "custom_name": "Паспорт Пышки"
}
```
Примечание:
- `custom_name` опционален;
- если `custom_name` не задан, backend использует имя типа документа и при необходимости добавляет суффикс для уникальности.

Response `200`:
```json
{
  "custom_name": "pasport_pyshki",
  "object_key": "string",
  "upload_url": "string",
  "expires_in": 900
}
```

### 8.4 `POST /pets/{pet_id}/documents/complete`
Назначение:
Подтвердить завершение загрузки документа.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Request:
```json
{
  "document_type_id": 1,
  "object_key": "string",
  "custom_name": "Паспорт Пышки"
}
```
Примечание:
- `custom_name` опционален;
- если `custom_name` передан, он должен соответствовать ранее выданному `upload-url` (с учётом нормализации имени).

Response `200`:
- `PetDocumentResponse`

### 8.5 `PATCH /pets/{pet_id}/documents/{document_row_id}`
Назначение:
Обновить метаданные документа.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Request:
```json
{
  "document_type_id": 2,
  "custom_name": "Главная справка"
}
```

Примечание:
- пользователь может менять и `custom_name`, и `document_type_id`;
- если `custom_name` не передан при загрузке, backend использует имя типа документа по умолчанию;
- в ответах `custom_name` соответствует имени файла без расширения, сформированному на этапе `upload-url`.

### 8.6 `GET /pets/{pet_id}/documents/{document_row_id}/download-url`
Назначение:
Получить временный URL для скачивания документа.

Auth:
- требуется bearer token

Access:
- владелец или shared user

Response `200`:
```json
{
  "document_id": 1,
  "document_type_name": "Veterinary passport",
  "custom_name": "veterinary_passport",
  "object_key": "string",
  "download_url": "string",
  "expires_in": 300
}
```

### 8.7 `DELETE /pets/{pet_id}/documents/{document_row_id}`
Назначение:
Удалить документ.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Response `200`:
```json
{
  "deleted": true
}
```

## 9. Sharing API

### 9.1 `POST /invites`
Назначение:
Создать приглашение на доступ к питомцу.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Request:
```json
{
  "pet_id": 1,
  "max_uses": 1,
  "expires_at": "2026-12-31T23:59:59Z"
}
```

Response `201`:
```json
{
  "invite_url": "https://example.com/invite/abc123",
  "invite_code": "abc123"
}
```

### 9.2 `GET /invites?invite_code=...`
Назначение:
Получить данные приглашения.

Auth:
- не требуется

Response `200`:
- `InviteResponse`

### 9.3 `DELETE /invites?invite_code=...`
Назначение:
Деактивировать приглашение.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Response `200`:
```json
{
  "success": true
}
```

### 9.4 `POST /invites/accept`
Назначение:
Принять приглашение.

Auth:
- требуется bearer token

Request:
```json
{
  "invite_code": "abc123"
}
```

Response `202`:
```json
{
  "message": "Invite accepted succesfully"
}
```

### 9.5 `GET /pets/{pet_id}/shared-users`
Назначение:
Получить список пользователей с доступом к питомцу.

Auth:
- требуется bearer token

Access:
- в текущем backend только владелец питомца

Response `200`:
```json
[
  {
    "pet_id": 1,
    "pet_name": "Milo",
    "shared_with_user_id": 10,
    "shared_with_user_name": "Anna",
    "shared_till": null
  }
]
```

### 9.6 `DELETE /pets/{pet_id}/access/{user_id}`
Назначение:
Отозвать доступ у конкретного пользователя.

Auth:
- требуется bearer token

Access:
- только владелец питомца

Response `200`:
```json
{
  "success": true
}
```

## 10. Map API

### 10.1 `GET /map-points/vet-clinics`
Назначение:
Получить активные точки ветклиник.

Auth:
- не требуется

Response `200`:
```json
[
  {
    "id": 1,
    "vet_name": "Vet Clinic",
    "vet_lat": 55.75,
    "vet_lon": 37.61,
    "vet_working_hours": "10:00-22:00",
    "vet_is_24_7": "нет",
    "vet_street": "Tverskaya",
    "vet_building_number": "1",
    "vet_phone": "+79990000000"
  }
]
```

### 10.2 `GET /map-points/dogfriendly-places`
Назначение:
Получить активные точки dog-friendly мест.

Auth:
- не требуется

Response `200`:
```json
[
  {
    "id": 1,
    "dogfriendly_place_name": "Cafe",
    "dogfriendly_place_lat": 55.75,
    "dogfriendly_place_lon": 37.61,
    "dogfriendly_place_working_hours": "09:00-23:00",
    "dogfriendly_place_is_24_7": "нет",
    "dogfriendly_place_street": "Arbat",
    "dogfriendly_place_building_number": "5"
  }
]
```

## 11. LLM Chat API

### 11.1 `POST /llm-chat`
Назначение:
Создать чат.

Auth:
- требуется bearer token

Request:
```json
{
  "chat_title": "New Chat"
}
```

Response `200`:
```json
{
  "id": 1,
  "chat_title": "New Chat",
  "created_at": "2026-01-01T10:00:00Z"
}
```

### 11.2 `GET /llm-chat`
Назначение:
Получить список чатов текущего пользователя.

Auth:
- требуется bearer token

Response `200`:
- `ChatResponse[]`

### 11.3 `GET /llm-chat/{chat_id}/messages`
Назначение:
Получить сообщения чата.

Auth:
- требуется bearer token

Response `200`:
- `MessageResponse[]`

### 11.4 `POST /llm-chat/{chat_id}/messages`
Назначение:
Отправить сообщение в чат.

Auth:
- требуется bearer token

Request:
```json
{
  "content": "How should I care for my dog?"
}
```

Response `200`:
```json
{
  "user_message": {
    "id": 1,
    "chat_id": 1,
    "role": "user",
    "content": "How should I care for my dog?",
    "created_at": "2026-01-01T10:00:00Z"
  },
  "assistant_message": {
    "id": 2,
    "chat_id": 1,
    "role": "assistant",
    "content": "Response text",
    "created_at": "2026-01-01T10:00:02Z"
  }
}
```

## 12. Admin / Import API

### 12.1 `POST /upload-data/import-vet-csv`
### 12.2 `POST /upload-data/import-dogplace-csv`
Назначение:
Импорт CSV-данных для карты.

Auth:
- по целевой модели должен быть доступен только `admin`

Формат:
- `multipart/form-data`
- поле `file`

Response `200`:
```json
{
  "total_rows": 10,
  "imported_rows": 8,
  "skipped_rows": 2,
  "errors": [
    {
      "row_number": 3,
      "error": "Validation error",
      "raw_data": {}
    }
  ]
}
```

Примечание:
- административная защита для этих маршрутов должна быть явно усилена.

## 13. Расхождения с целевой моделью

### 13.1 Pet-centric chat
Целевая модель:
- чат должен быть привязан к питомцу.

Текущее API:
- `llm-chat` сейчас user-centric и не принимает `pet_id`.

### 13.2 Shared user и чат
Целевая модель:
- `shared_user` должен иметь доступ к ИИ-чату питомца.

Текущее API:
- чат доступен только владельцу user-owned chat.

### 13.3 Shared user и sharing UI
Целевая модель:
- `shared_user` получает почти все сценарии по питомцу, кроме редактирования и управления шарингом.

Текущее API:
- просмотр питомца и документов уже есть;
- просмотр списка shared users для `shared_user` не реализован как подтвержденный контракт.

### 13.4 Map personalization
Целевая модель:
- карта должна поддерживать фильтры и определение города пользователя.

Текущее API:
- отдает просто активные точки, без пользовательского контекста.

## 14. Что желательно уточнить дальше
- точные лимиты размеров файлов;
- отдельный formal error catalog по доменным кодам ошибок;
- итоговую auth-стратегию хранения refresh token на клиенте;
- будущий контракт pet-centric LLM chat;
- итоговую admin-модель для import endpoints.

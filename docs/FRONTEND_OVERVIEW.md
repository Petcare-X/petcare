# Frontend Overview

## Назначение фронтенда

Frontend в `apps/frontend` отвечает за пользовательский интерфейс приложения PetCare и покрывает основные пользовательские сценарии:

- регистрация, вход и восстановление клиентской сессии
- просмотр и редактирование профиля пользователя
- создание, просмотр и редактирование профилей питомцев
- загрузка, скачивание и удаление документов питомца
- загрузка фотографий питомца
- шеринг доступа к питомцу через invite-code
- просмотр карты с dog-friendly местами, клиниками и салонами
- работа с AI-чатом, привязанным к питомцу

Иными словами, фронтенд является основным клиентским приложением для владельца питомца и пользователей, которым выдан доступ по шерингу.

## Технологический стек

### Основные технологии

- `React 19`
- `TypeScript`
- `Vite`
- `TanStack Router`
- `TanStack React Query`
- `Axios`
- `React Hook Form`
- `Zod`

### Дополнительные технологии

- `vite-plugin-pwa` для PWA-режима
- `@yandex/ymaps3-types` и загрузка `Yandex Maps JS API v3`
- `@tailwindcss/vite` и `tailwindcss`

Важно: Tailwind подключен на уровне toolchain, но текущий UI в основном реализован через обычные CSS-файлы, а не через массовое использование utility-классов.

### Что есть в зависимостях, но почти не участвует в текущей архитектуре

- `zustand` установлен, но в проанализированном коде практически не используется как основной state layer

## Общая архитектура

Frontend организован по слоям, близким к feature-sliced подходу:

- `app` — точка входа, провайдеры, роутинг, глобальные стили
- `pages` — экранные контейнеры и page-level composition
- `features` — пользовательские сценарии и интерактивные куски логики
- `entities` — доменные сущности и их API/model-слои
- `widgets` — переиспользуемые составные UI-блоки
- `shared` — инфраструктурный и общий код

Это хороший базовый каркас для среднеразмерного SPA.

## Структура по слоям

### `app`

Слой `app` отвечает за инициализацию приложения:

- `src/app/main.tsx` — точка монтирования React
- `src/app/providers/index.tsx` — композиция провайдеров
- `src/app/providers/query-provider.tsx` — инициализация `React Query`
- `src/app/providers/router-provider.tsx` — подключение `TanStack Router`
- `src/app/providers/auth-bootstrap.tsx` — восстановление сессии при старте
- `src/app/router/routes.tsx` — дерево маршрутов
- `src/app/router/guards.tsx` — route guards для auth/guest flow

#### Что происходит на старте

1. Создается `QueryClient`
2. Выполняется `AuthBootstrap`
3. Если пользователь еще не определен, фронт пытается обновить access token через `/auth/refresh`
4. После этого рендерится роутер и защищенные маршруты

## Роутинг

Роутинг реализован на `TanStack Router`.

Основные маршруты:

- `/` и `/login` — логин
- `/signup` — регистрация
- `/home` — главный экран
- `/pets/$petId` — профиль питомца
- `/pets/$petId/edit` — редактирование питомца
- `/pets/$petId/documents/` — документы питомца
- `/user` — профиль пользователя
- `/user/edit` — редактирование профиля
- `/map` — карта
- `/calendar` — календарь
- `/chat` / `/chat/$petId` / `/chat/$petId/$chatId` — чатовые сценарии

Также есть layout-слои:

- `FullAppShell`
- `MainOnlyShell`
- `NavbarOnlyShell`

Это позволяет использовать разные оболочки для разных экранов без дублирования layout-логики.

## Слой API и работа с сетью

Центральная точка для HTTP-запросов — `src/shared/api/client.ts`.

### Особенности API-клиента

- базовый URL: `import.meta.env.VITE_API_BASE_URL ?? "/api"`
- `withCredentials: true`
- access token добавляется в `Authorization` header
- есть interceptor на `401`, который:
  - вызывает `/auth/refresh`
  - сохраняет новую сессию
  - повторяет исходный запрос

### Почему это важно

Фронтенд реализует смешанную модель auth:

- access token живет на клиенте
- refresh flow завязан на cookie backend
- фронт использует same-origin API через `/api`

Эта схема позволяет избежать множества CORS-проблем и упрощает локальный и production запуск.

## Работа с данными

Основной data layer построен на `TanStack React Query`.

Типичный паттерн в проекте:

- `entities/*/api/*.api.ts` — низкоуровневые HTTP-функции
- `entities/*/model/*.queries.ts` — query hooks
- `features/*/model/use-*.ts` — mutation hooks и orchestration логика

### Примеры доменных query/mutation потоков

- питомцы:
  - `entities/pet/api/pet.api.ts`
  - `entities/pet/model/pet.queries.ts`
- документы:
  - `entities/document/api/document.api.ts`
  - `entities/document/model/document.queries.ts`
- чат:
  - `entities/chat/api/chat.api.ts`
  - `entities/chat/model/chat.queries.ts`
  - `entities/chat/model/chat.mutations.ts`

### Характерная особенность

Фронтенд активно использует `invalidateQueries` после мутаций, чтобы синхронизировать UI с backend-состоянием.

## Доменные области фронтенда

### Пользователь и авторизация

Фронтенд отвечает за:

- signup
- login
- logout
- bootstrap существующей сессии
- запрос профиля `GET /users/me`
- удаление аккаунта

Ключевые файлы:

- `entities/auth/api/auth.api.ts`
- `features/auth/model/use-login.ts`
- `features/auth/model/use-logout.ts`
- `entities/user/api/user.api.ts`

### Питомцы

Питомец — центральная доменная сущность интерфейса.

Фронтенд покрывает:

- список питомцев
- карточки питомцев
- профиль питомца
- редактирование питомца
- загрузку фото
- справочник пород

Ключевые файлы:

- `entities/pet/api/pet.api.ts`
- `entities/pet/api/animal-reference.api.ts`
- `entities/pet/api/pet-photo.api.ts`
- `widgets/pet-card/*`
- `pages/pets/*`

### Документы питомца

Подсистема документов включает:

- список документов
- загрузку документа
- получение presigned upload URL
- загрузку файла напрямую в storage
- подтверждение завершения загрузки
- скачивание документа
- удаление документа

Ключевой момент: фронтенд не грузит файл через backend-тело целиком. Он работает в двух шагах:

1. получает upload URL от backend
2. загружает файл напрямую в object storage
3. завершает upload через backend, который сохраняет метаданные

Это важная часть взаимодействия с остальными слоями приложения.

### Шеринг питомца

Фронтенд умеет:

- создавать invite code
- принимать invite code
- показывать число пользователей, которым расшарен питомец

Ключевые файлы:

- `entities/invite/api/invite.api.ts`
- `entities/invite/api/shared-users.api.ts`
- `features/manage-share/*`

### Карта

Карта — отдельная feature area с уже вынесенной внутренней структурой:

- `features/map/model/*`
- `features/map/ui/*`
- `features/map/lib/*`

Фронтенд:

- получает точки карты из backend
- нормализует разные типы мест в единый `MapPlace`
- отображает Yandex Map
- рендерит кастомные маркеры
- показывает bottom sheet со списком мест
- фильтрует и ищет места
- использует геолокацию пользователя

### AI-чат

Фронтенд взаимодействует с backend-чатом через `/llm-chat/*` endpoints:

- список чатов питомца
- история сообщений
- создание нового чата
- удаление чата
- отправка сообщений

Клиентский чат не общается напрямую с LLM-provider. Вся работа с моделью инкапсулирована на backend.

## Взаимодействие с остальными частями приложения

### 1. Взаимодействие с backend API

Это основной способ интеграции.

Фронтенд обращается к backend для:

- авторизации
- CRUD-потоков по питомцам
- работы с документами
- создания и принятия invite
- запросов по карте
- чатов
- получения user profile

Архитектурно backend для фронта — основной источник доменного состояния.

### 2. Взаимодействие с object storage

Фронтенд взаимодействует с object storage не напрямую по бизнес-логике, а через presigned URLs, выданные backend.

Это используется для:

- загрузки документов
- загрузки фото
- скачивания документов
- получения download URLs для фото

Практически это означает:

- backend остается владельцем правил доступа
- storage остается техническим transport-слоем
- фронтенд не должен знать внутреннюю структуру хранилища глубже object URLs и object keys

### 3. Взаимодействие с Yandex Maps

Фронтенд напрямую загружает `Yandex Maps JS API v3`:

- `shared/lib/loadYmaps3.ts`
- `shared/lib/ymaps.ts`

Эта интеграция чисто фронтовая:

- backend отдает сами map points
- frontend отвечает за визуализацию карты и маркеров

### 4. Взаимодействие с Telegram/Bot-частью

Прямой tight coupling с ботом на фронте минимален.

Фронтенд участвует в сценариях, которые логически связаны с ботом:

- работа с invite code
- пользовательские данные и auth context

Но сам frontend не является UI для Telegram-бота и не оркестрирует бот-логику напрямую.

## Взаимодействие в dev/prod среде

### Локальная разработка

В dev используется Vite proxy:

- фронт работает на `5173`
- API идет через `/api`
- proxy target задается через `VITE_DEV_PROXY_TARGET`

Это позволяет:

- упростить auth/refresh flow
- не бить из браузера в отдельный origin вручную
- уменьшить CORS-проблемы

### Docker dev

В Docker proxy target должен указывать не на `localhost`, а на `backend:8000`.

Текущая конфигурация фронта и `docker-compose` это уже учитывает.

### Production

Во фронтенде также есть production-сценарий:

- `Dockerfile.prod`
- `nginx.conf`
- PWA manifest

Production-модель предполагает same-origin API через `/api`, что соответствует и локальной dev-схеме.

## Состояние UI-архитектуры

Сильные стороны текущего фронта:

- есть внятное разделение на `entities / features / pages / widgets / shared`
- React Query используется последовательно
- API-слой достаточно централизован
- карта уже вынесена в feature-level модули
- роутинг и layout-композиция оформлены аккуратно

Что важно учитывать:

- в `src` есть заметное количество пустых или заготовочных файлов
- часть shared UI abstractions пока не стала реальным design-system слоем
- Tailwind подключен, но проект по факту опирается в основном на hand-written CSS

Это не критично, но полезно понимать как текущую точку эволюции проекта.

## Найденные заготовки и потенциальный техдолг

В проекте есть ряд пустых файлов, например:

- `src/app/App.tsx`
- `src/app/providers/theme-provider.tsx`
- `src/shared/ui/button.tsx`
- `src/shared/ui/dialog.tsx`
- `src/shared/ui/sheet.tsx`
- `src/shared/config/env.ts`
- `src/shared/hooks/use-auth.ts`
- ряд файлов в `features/manage-share`, `features/update-document`, `features/link-telegram`

Это выглядит как следы незавершенного рефакторинга или подготовленных, но не доведенных abstractions.

Рекомендация:

- либо заполнить эти файлы реальной логикой
- либо удалить лишние заготовки, чтобы они не создавали ложное впечатление завершенной инфраструктуры

## Краткое резюме

Frontend PetCare — это SPA-клиент на React + TypeScript, который:

- управляет auth и пользовательской сессией
- работает с питомцами, фото и документами
- реализует шеринг доступа к питомцу
- визуализирует карту с местами и геолокацией
- предоставляет чатовый интерфейс к backend AI-модулю

Технологически фронт опирается на:

- Vite
- TanStack Router
- TanStack React Query
- Axios
- React Hook Form + Zod
- PWA и Yandex Maps

По архитектуре это уже не монолитный “один большой React-приложение”, а достаточно хорошо разделенный клиент с доменными модулями. При этом в кодовой базе еще есть следы незавершенной внутренней стандартизации, которые можно постепенно убрать без изменения бизнес-логики.

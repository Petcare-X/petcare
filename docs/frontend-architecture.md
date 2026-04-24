# Frontend Architecture: PetCare

## 1. Назначение документа
Этот документ описывает техническую архитектуру frontend-части PetCare.

Он отвечает на вопросы:
- на каком стеке строится клиент;
- как организованы маршруты, состояние и взаимодействие с backend;
- как реализуется PWA-подход для web и Android;
- как структурировать код, UI и интеграции.

Продуктовые требования находятся в `docs/PRD.md`.
Архитектура backend находится в `docs/backend-architecture.md`.

## 2. Архитектурные цели frontend
- Построить один клиент для web и Android-сценария использования через PWA.
- Сохранить mobile-first UX как основной сценарий.
- Обеспечить быструю работу CRUD-сценариев, загрузки документов, карты и чата.
- Упростить поддержку кодовой базы за счет предсказуемой структуры и разделения server state и UI state.
- Минимизировать дублирование логики между экранами и пользовательскими потоками.
- Поддержать стратегическую публикацию приложения через `Google Play` и `RuStore`.
- На первой версии сфокусироваться на `Android + web`, без обязательного равноправного `iOS`-сценария.
- Сделать интерфейс понятным для новичков и полезным в непредвиденных ситуациях, поездках и при смене места жительства.

## 3. Рекомендуемый стек

Примечание по текущему состоянию:
- базовый frontend-проект уже поднят в `apps/frontend`;
- фактически установлены `React 19`, `TypeScript 6`, `Vite 7`, `TanStack Router`, `TanStack Query`, `Zustand`, `React Hook Form`, `Zod`, `Tailwind CSS`, `vite-plugin-pwa` и `axios`;
- интеграция карт пока не установлена как библиотека и будет выбрана отдельно на следующем этапе.

### 3.1 Базовый стек
- Фреймворк: `React`
- Язык: `TypeScript`
- Сборка и dev server: `Vite`
- PWA: `vite-plugin-pwa`

### 3.2 Навигация и состояние
- Роутинг: `TanStack Router`
- Server state: `TanStack Query`
- Локальное UI state: `Zustand`
- Формы: `React Hook Form`
- Валидация: `Zod`

### 3.3 UI и стили
- Стилизация: `Tailwind CSS`

### 3.4 Интеграции
- HTTP-клиент: `axios`
- Карты: выбор конкретной библиотеки пока отложен; целевой сценарий остается `Yandex Maps`
- Аналитика: решение пока не зафиксировано

## 4. Почему такая архитектура подходит проекту
- Backend уже существует как отдельный `FastAPI` API, поэтому frontend должен быть самостоятельным клиентом, а не fullstack-framework-слоем.
- Основные пользовательские сценарии происходят после логина, а не завязаны на SEO-страницы.
- Продукт ориентирован на app-like experience: карточки питомцев, документы, карта, чат, профиль.
- PWA-подход позволяет закрыть цель "web + Android" без поддержки двух отдельных frontend-кодовых баз.

## 5. Основные frontend-модули

### 5.1 Auth
Отвечает за:
- логин;
- регистрацию;
- альтернативный вход через Telegram;
- хранение и обновление сессии;
- защиту приватных роутов;
- обработку logout и logout-all.

### 5.2 Pets
Отвечает за:
- список питомцев;
- создание питомца;
- просмотр карточки;
- редактирование;
- удаление;
- переключение между owned/shared карточками.

### 5.3 Documents
Отвечает за:
- список документов питомца;
- загрузку через presigned URL flow;
- завершение загрузки;
- скачивание и удаление документа.

### 5.4 Photos
Отвечает за:
- загрузку фото питомца;
- завершение загрузки;
- отображение актуального изображения;
- удаление или замену фото.

### 5.5 Sharing
Отвечает за:
- создание invite-ссылки;
- отображение пользователей с доступом;
- принятие приглашения;
- отзыв доступа.

### 5.6 Map
Отвечает за:
- отображение карты;
- переключение между типами точек;
- загрузку и кэширование точек;
- карточку выбранного места;
- фильтрацию;
- определение города пользователя по геоданным без использования точного местоположения;
- поиск;
- поддержку сценариев использования в поездке, новом городе или после переезда.

### 5.7 LLM Chat
Отвечает за:
- список чатов по питомцу;
- отображение истории сообщений;
- отправку сообщений;
- состояния генерации ответа;
- обработку ошибок внешней AI-интеграции через backend;
- явное подключение данных профиля питомца как контекста по выбору пользователя;
- поддержку сценариев для новичков и нештатных ситуаций, когда пользователю нужен быстрый и понятный ответ.

### 5.8 Profile
Отвечает за:
- получение профиля пользователя;
- изменение данных и контактов;
- управление сессией;
- удаление аккаунта.

## 6. Структура проекта

```text
frontend/
  public/
    manifest.webmanifest
    favicon.svg
    icons/
  src/
    app/
      App.tsx
      main.tsx
      providers/
        index.tsx
        router-provider.tsx
        query-provider.tsx
        theme-provider.tsx
      router/
        index.tsx
        routes.tsx
        guards.tsx
      styles/
        globals.css
        theme.css
    pages/
      auth/
        login-page.tsx
        register-page.tsx
      onboarding/
        onboarding-page.tsx
      pets/
        pets-list-page.tsx
        pet-details-page.tsx
        edit-pet-page.tsx
      documents/
        pet-documents-page.tsx
      sharing/
        pet-sharing-page.tsx
        invite-page.tsx
      map/
        map-page.tsx
      profile/
        profile-page.tsx
    widgets/
      app-shell/
        app-shell.tsx
        page-header.tsx
      pet-card/
        pet-card.tsx
        pet-summary.tsx
      document-list/
        document-list.tsx
        document-list-item.tsx
      sharing-panel/
        sharing-panel.tsx
      map-panel/
        map-panel.tsx
        map-filters.tsx
    features/
      auth/
        ui/
          login-form.tsx
          register-form.tsx
          telegram-login-button.tsx
        model/
          use-login.ts
          use-register.ts
          use-logout.ts
      create-pet/
        ui/
          create-pet-form.tsx
        model/
          use-create-pet.ts
          create-pet.schema.ts
      edit-pet/
        ui/
          edit-pet-form.tsx
        model/
          use-update-pet.ts
          edit-pet.schema.ts
      upload-photo/
        ui/
          pet-photo-upload.tsx
        model/
          use-upload-pet-photo.ts
      upload-document/
        ui/
          upload-document-form.tsx
        model/
          use-upload-document.ts
          upload-document.schema.ts
      update-document/
        ui/
          update-document-form.tsx
        model/
          use-update-document.ts
          update-document.schema.ts
      manage-share/
        ui/
          create-invite-button.tsx
          shared-users-list.tsx
        model/
          use-create-invite.ts
          use-revoke-access.ts
      filter-map/
        ui/
          map-filter-form.tsx
        model/
          map-filter.store.ts
    entities/
      user/
        api/
          user.api.ts
        model/
          user.types.ts
          user.queries.ts
      pet/
        api/
          pet.api.ts
          pet-photo.api.ts
          animal-reference.api.ts
        model/
          pet.types.ts
          pet.queries.ts
      document/
        api/
          document.api.ts
        model/
          document.types.ts
          document.queries.ts
      invite/
        api/
          invite.api.ts
        model/
          invite.types.ts
          invite.queries.ts
      map-point/
        api/
          map.api.ts
        model/
          map.types.ts
          map.queries.ts
    shared/
      api/
        client.ts
        auth-session.ts
        error-map.ts
      config/
        env.ts
      lib/
        cn.ts
        date.ts
        file.ts
      ui/
        button.tsx
        input.tsx
        select.tsx
        dialog.tsx
        sheet.tsx
        spinner.tsx
        empty-state.tsx
      hooks/
        use-auth.ts
        use-current-pet.ts
      types/
        api.ts
        common.ts
      constants/
        routes.ts
        query-keys.ts
```

### Пояснение по слоям
- `app/` содержит инфраструктуру приложения: провайдеры, роутер, query client и глобальную инициализацию.
- `pages/` содержит маршрутные экраны и экранные композиции.
- `widgets/` содержит крупные составные UI-блоки.
- `features/` содержит пользовательские действия и прикладные флоу.
- `entities/` содержит доменные типы, адаптеры и небольшие переиспользуемые элементы вокруг бизнес-логики.
- `shared/` хранит переиспользуемую инфраструктуру и базовые UI-элементы.

## 7. Роутинг

### 7.1 Основные маршруты
- `/auth/login`
- `/auth/register`
- `/onboarding`
- `/pets`
- `/pets/:petId`
- `/pets/:petId/documents`
- `/pets/:petId/sharing`
- `/pets/:petId/chat`
- `/pets/:petId/chat/:chatId`
- `/map`
- `/profile`
- `/invite/:inviteCode`

### 7.2 Правила роутинга
- приватные роуты защищаются auth guard;
- после логина пользователь перенаправляется на список питомцев;
- если у пользователя нет питомцев, возможен redirect в onboarding;
- invite links должны открываться в приложении и приводить к сценарию принятия приглашения;
- onboarding должен быть особенно дружелюбным для пользователей с минимальным опытом ухода за питомцем.

## 8. Управление состоянием

### 8.1 Что хранится в server state
- профиль текущего пользователя;
- список питомцев;
- карточка питомца;
- документы питомца;
- shared users;
- приглашения;
- список чатов по питомцу;
- сообщения чата;
- map points;
- document types.

Эти данные должны жить в `TanStack Query`.

### 8.2 Что хранится в локальном UI state
- активный экранный контекст и временные UI-переключатели;
- текущее состояние модалок и drawer;
- временные фильтры карты;
- выбранный питомец в текущей сессии;
- transient upload states;
- черновики форм, если они не привязаны к library-managed form state.

Эти данные должны жить в `Zustand` или локальном state компонентов.

### 8.3 Стратегия кэширования
- `stale-while-revalidate` для профиля, списка питомцев, чатов и карты;
- инвалидация кэша после мутаций;
- краткоживущий cache для upload/download URLs;
- optimistic updates допустимы для небольших PATCH-операций;
- последние пользовательские данные должны кэшироваться локально для PWA-сценариев в ограниченном объеме: карточка питомца, параметры питомца, количество пользователей с доступом и последние сообщения ИИ-чата.

## 9. Формы и валидация
- Все пользовательские формы строятся на `React Hook Form`.
- Валидация должна быть описана через `Zod`.
- Форма питомца должна отражать ограничения backend-схем и не допускать очевидно некорректных значений.
- Ошибки валидации должны быть отображены рядом с полями и не требовать чтения общего alert-блока.
- Регистрация, логин, профиль пользователя, создание питомца, загрузка документов и принятие приглашения должны иметь отдельные form schemas.
- Формы и подсказки должны быть понятны новичкам и не предполагать наличия экспертных знаний по уходу за питомцами.

## 10. API-взаимодействие

### 10.1 Общие принципы
- frontend работает только с backend API и не обращается к object storage напрямую, кроме presigned upload/download flows;
- все запросы должны проходить через единый api client layer;
- ошибки должны нормализоваться в единый frontend-friendly формат.

### 10.2 Базовый API-контракт

Auth:
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/logout-all`
- `POST /auth/telegram`

Users:
- `POST /users`
- `GET /users/me`
- `PATCH /users/me/data`
- `PATCH /users/me/contacts`
- `DELETE /users/me`

Reference data:
- `GET /animal-types`
- `GET /animal-types/{animal_type_id}/breeds`

Pets:
- `GET /pets`
- `POST /pets`
- `GET /pets/{pet_id}`
- `PATCH /pets/{pet_id}`
- `DELETE /pets/{pet_id}`

Pet photo:
- `POST /pets/{pet_id}/photo/upload-url`
- `POST /pets/{pet_id}/photo/complete`
- `GET /pets/{pet_id}/photo/download-url`
- `DELETE /pets/{pet_id}/photo`

Documents:
- `GET /document-types`
- `GET /pets/{pet_id}/documents`
- `POST /pets/{pet_id}/documents/upload-url`
- `POST /pets/{pet_id}/documents/complete`
- `PATCH /pets/{pet_id}/documents/{document_row_id}`
- `GET /pets/{pet_id}/documents/{document_row_id}/download-url`
- `DELETE /pets/{pet_id}/documents/{document_row_id}`

Sharing:
- `POST /invites`
- `GET /invites?invite_code=...`
- `DELETE /invites?invite_code=...`
- `POST /invites/accept`
- `GET /pets/{pet_id}/shared-users`
- `DELETE /pets/{pet_id}/access/{user_id}`

Map:
- `GET /map-points/vet-clinics`
- `GET /map-points/dogfriendly-places`

LLM chat:
- `POST /llm-chat`
- `GET /llm-chat`
- `GET /llm-chat/{chat_id}/messages`
- `POST /llm-chat/{chat_id}/messages`

Наблюдения:
- frontend должен работать с текущими маршрутами backend без префикса `api/v1` на данном этапе;
- маршруты и query keys желательно инкапсулировать в одном слое для будущего versioning без массовых правок по приложению.

### 10.3 Обработка ошибок
Frontend должен единообразно обрабатывать:
- ошибки авторизации;
- ошибки валидации;
- сетевые ошибки;
- ошибки истекшей сессии;
- ошибки presigned upload flow;
- ошибки внешней LLM-интеграции, возвращенные backend.

## 11. Auth flow на фронте

### 11.1 Текущее ожидание
- access token хранится в памяти приложения; [ДОПУЩЕНИЕ]
- refresh token хранится в более безопасном механизме, предпочтительно не в `localStorage`; [ДОПУЩЕНИЕ]
- все защищенные запросы отправляются с bearer token.

### 11.2 Поведение при истечении access token
1. клиент получает `401`;
2. пытается выполнить `refresh`;
3. при успехе повторяет исходный запрос;
4. при провале refresh переводит пользователя на логин и очищает клиентскую сессию.

### 11.3 Защита роутов
- приватные экраны доступны только при валидной сессии;
- неавторизованный пользователь не должен видеть приватные данные даже кратковременно на hydration/navigation;
- `shared user` может пользоваться почти всеми сценариями по питомцу, кроме редактирования данных питомца и управления шарингом;
- `shared user` имеет доступ к документам, карте, рекомендациям и ИИ-чату питомца.

## 12. PWA-стратегия

### 12.1 Цели PWA
- installable experience на Android;
- быстрый повторный вход в приложение;
- базовая устойчивость к нестабильной сети;
- ощущение "нативного" приложения без отдельной Android-кодовой базы.

### 12.2 Что должно быть реализовано
- `manifest.webmanifest`;
- набор иконок для установки;
- service worker;
- offline fallback page;
- кэширование app shell;
- поддержка install prompt там, где это возможно;
- splash-friendly launch experience на Android.

Целевой сценарий распространения:
- PWA должна проектироваться с учетом последующей публикации через `Google Play` и `RuStore`.

Офлайн-объем первой версии:
- карточка питомца;
- параметры и характеристики питомца;
- количество пользователей, которым питомец доступен;
- последние сообщения в чате с ИИ по питомцу.

Пользовательский смысл офлайн-режима:
- сохранить доступ к самой важной информации о питомце в поездке, новом месте или при нестабильной сети.

### 12.3 Что не следует обещать на старте
- полный offline-first для всех данных;
- надежную фоновую синхронизацию всех пользовательских изменений;
- полный parity с нативными Android APIs.

## 13. Производительность
- Целевые метрики: `LCP < 2.5s`, `INP < 200ms`, `CLS < 0.1`.
- Initial JS bundle первого экрана желательно держать в пределах до `220 KB gzip`. [ДОПУЩЕНИЕ]
- Карта, чат и документы должны грузиться через route-level lazy loading.
- Тяжелые зависимости карт и файловых превью не должны попадать в стартовый бандл.
- Изображения питомцев при необходимости могут проходить client-side compression перед upload. [ДОПУЩЕНИЕ]

## 14. Доступность
- Целевой уровень: `WCAG 2.1 AA`.
- Все формы должны быть доступны с клавиатуры.
- Все интерактивные элементы должны иметь accessible labels.
- Модалки, drawers и dropdowns должны иметь корректный focus management.
- Карта должна иметь альтернативный способ доступа к данным через список точек.

## 15. Безопасность frontend
- Не использовать `dangerouslySetInnerHTML` без крайне явной причины.
- Не хранить access token в `localStorage`.
- Ограничивать типы и размеры файлов до отправки.
- Защищать приложение от случайной утечки приватных данных через клиентские логи. [ДОПУЩЕНИЕ]
- Корректно очищать клиентскую сессию при logout и revoke ситуации.
- Поддерживать только форматы документов `PDF`, `JPG`, `PNG` на первой версии.
- Точные лимиты размера файлов для фото и документов пока не зафиксированы и должны быть согласованы отдельно.

## 16. Дизайн-система

### 16.1 Цветовая палитра
- Primary: `#F5F5F5`
- Brand color: `#F97316`
- Accent: `#EA580C`
- Success: `#2D8F5A`
- Warning: `#D98E04`
- Error: `#C44536`
- Text: `#313131`
- Subtext: `#969696`

### 16.2 Типографика
- Основной шрифт: `Nunito`
- Базовая шкала размеров:
  - `12px`
  - `14px`
  - `16px`
  - `18px`
  - `20px`
  - `24px`
  - `32px`

### 16.3 Базовый компонентный кит
- `Button`
- `IconButton`
- `Input`
- `PasswordInput`
- `Textarea`
- `Select`
- `DatePicker`
- `Checkbox`
- `Switch`
- `FormField`
- `ErrorMessage`
- `Card`
- `Avatar`
- `Badge`
- `Tabs`
- `Dialog`
- `Drawer / BottomSheet`
- `Toast`
- `Tooltip`
- `DropdownMenu`
- `Skeleton`
- `EmptyState`
- `FileUploader`
- `ProgressBar`
- `ChatBubble`
- `MessageComposer`
- `MapMarker`
- `FilterChip`
- `SearchBar`
- `ConfirmDialog`

## 17. Правила развития frontend
- Все новые пользовательские сценарии сначала должны быть согласованы с `PRD`.
- Все изменения, влияющие на API-взаимодействие, должны сверяться с `backend-architecture.md` и фактическим контрактом backend.
- Крупные новые фичи должны добавляться как отдельные `features/` или `entities/`, а не в случайные shared-компоненты.
- Доменные сущности должны оставаться источником истины для типов и бизнес-терминов на клиенте.
- Решение по `Capacitor` отложено и будет приниматься позже на основе ограничений PWA.

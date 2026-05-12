# PetCare — Frontend Developer

## Краткое описание проекта
`PetCare` — mobile-first `PWA`-приложение для владельцев домашних животных, которое объединяет цифровой профиль питомца, документы, совместный доступ, карту ветеринарных клиник и pet-friendly мест, а также `AI`-помощника.

Проект ориентирован на web и Android-сценарии использования через единый frontend-клиент.

## Роль
`Frontend Developer`

## Краткое описание работы
Отвечал за проектирование и развитие frontend-части `PetCare`: архитектуру клиентского приложения, маршрутизацию, интеграцию с backend API, формы, управление сессией и реализацию ключевых пользовательских экранов.

Работал на стыке frontend, продукта и backend-контракта: переводил пользовательские сценарии в структуру клиентского приложения, подготавливал удобные UI-потоки для мобильного использования и синхронизировал frontend-логику с текущей моделью API и прав доступа.

## Ключевые обязанности
- Спроектировал frontend-архитектуру приложения на `React 19`, `TypeScript`, `Vite`, `TanStack Router`, `TanStack Query`, `Zustand`, `React Hook Form`, `Zod`, `Tailwind CSS` и `vite-plugin-pwa`.
- Сформировал масштабируемую структуру проекта по слоям `app / pages / widgets / features / entities / shared`, чтобы разделить роутинг, бизнес-фичи, доменные сущности, UI и инфраструктурный код.
- Реализовал клиентскую маршрутизацию с публичными и защищенными роутами, layout-обвязками и `app shell` для основных продуктовых сценариев.
- Настроил frontend auth-flow: логин, регистрация, bootstrap пользовательской сессии, logout, protected routes и автоматическое обновление access token через refresh token flow.
- Реализовал API client на `axios` с интерсепторами, `Authorization` header, `withCredentials`-сценарием и обработкой повторного запроса после `401`.
- Построил слой server state на `TanStack Query` для работы с питомцами, документами, картой, инвайтами и пользовательскими данными.
- Реализовал формы и валидацию на `React Hook Form + Zod` для auth, создания и редактирования питомца, загрузки и обновления документов.
- Подготовил frontend-интеграцию с backend upload flow для фото и документов через presigned URL / complete-сценарии.
- Реализовал ключевые пользовательские страницы и экраны: auth, home, profile, pet details, documents, map, chat, sharing, onboarding, not-found.
- Спроектировал и собрал reusable UI-слой: `app shell`, header, navbar, pet cards, document list, sharing panel, map panel, empty states, form controls.
- Настроил работу с авторизованным API-клиентом для получения профиля пользователя, списка питомцев, справочников пород и других backend-данных.
- Синхронизировал frontend-реализацию с продуктовой документацией, `API contract`, `permission matrix` и архитектурными документами проекта.

## Ключевые результаты на текущем этапе
- Заложил полноценную основу frontend-клиента для `PetCare`: в проекте уже есть `125+` frontend-файлов в слоях `app`, `pages`, `widgets`, `features`, `entities`, `shared`.
- Собрал архитектурный каркас PWA-приложения с разделением экранов, фич, доменных API-модулей и общего UI, что упрощает дальнейшее масштабирование.
- Реализовал защищенную клиентскую навигацию и сессионную модель, при которой приложение умеет восстанавливать авторизацию через refresh flow и корректно работать с гостевыми и авторизованными сценариями.
- Подготовил frontend для основных продуктовых доменов: auth, pets, documents, sharing, map, profile и `AI chat`.
- Довел до рабочего состояния ключевые frontend-сценарии: логин/регистрация, просмотр и создание питомцев, профиль пользователя, документы, карта, чат и элементы совместного доступа.
- Построил слой API-интеграции и query-модель, который позволяет изолировать серверные вызовы, повторно использовать доменные запросы и управлять кэшированием клиентских данных.
- Подготовил frontend к интеграции со сложными backend-сценариями: bearer auth, refresh cookies, presigned upload/download, role-based access и доменными ограничениями API.

## Ключевые достижения
- Превратил набор продуктовых сценариев в структурированное клиентское приложение с понятной архитектурой, мобильным фокусом и базовой PWA-готовностью.
- Снизил риск рассинхронизации frontend и backend за счет опоры на `API contract`, `permission matrix`, архитектурные документы и alignment-артефакты.
- Обеспечил устойчивую модель авторизации на клиенте: bootstrap сессии, refresh token flow, повтор запросов после `401`, работа с `HttpOnly` cookie и разделение состояний `unknown/authenticated/guest`.
- Подготовил frontend под файловые сценарии продукта: загрузку и обновление документов, работу с фото питомцев и связанную доменную валидацию.
- Выстроил переиспользуемую UI-структуру и feature-layer подход, который упрощает развитие новых экранов и подключение дополнительных разработчиков.
- Заложил основу для развития продукта как единого web/PWA-клиента для Android и браузера без необходимости поддерживать отдельные клиентские кодовые базы.

## Короткая версия для резюме
`Frontend Developer — PetCare`

Разрабатывал frontend mobile-first `PWA`-приложения для владельцев домашних животных: проектировал архитектуру клиента, маршрутизацию, auth-flow, формы и интеграцию с backend API.

Построил frontend на `React + TypeScript + Vite` с `TanStack Router`, `TanStack Query`, `Zustand`, `React Hook Form`, `Zod`, `Tailwind CSS` и `axios`; реализовал protected routes, session bootstrap, refresh token flow, страницы ключевых доменов и слой API-интеграции.

Подготовил frontend под сценарии pets, documents, profile, sharing, map и `AI chat`, а также синхронизировал реализацию с `API contract`, permission rules и архитектурной документацией проекта.

## Короткие bullets
- Разработал frontend-архитектуру `PWA`-приложения на `React`, `TypeScript`, `Vite`, `TanStack Router`, `TanStack Query`, `Zustand`, `React Hook Form`, `Zod`, `Tailwind CSS`.
- Реализовал клиентскую маршрутизацию, protected routes, `app shell`, auth bootstrap и refresh token flow через `axios`-интерсепторы и `HttpOnly` cookie-сценарий.
- Собрал страницы и фичи для auth, pets, documents, profile, map, chat, sharing и onboarding, а также reusable UI-слой на уровне widgets/shared.
- Подготовил frontend-интеграцию с backend API, включая bearer auth, query-layer, presigned upload/download flow и работу с role-based access.
- Синхронизировал frontend-реализацию с `PRD`, `API contract`, `permission matrix`, architecture docs и alignment-документацией.

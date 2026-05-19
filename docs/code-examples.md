# Примеры кода для отчёта

Ниже собраны самые удачные фрагменты из проекта для вставки в отчёт. Я специально выбрал короткие и показательные примеры, которые хорошо подтверждают не только наличие кода, но и вашу собственную работу по интеграции frontend, backend, валидации, загрузке файлов и бизнес-логике.

## 5 лучших примеров для отчёта

### 1. Axios-клиент с refresh interceptor

- Путь к файлу: `apps/frontend/src/shared/api/client.ts`
- Что делает код:
  - создаёт общий `axios`-клиент;
  - подставляет `Authorization` header из access token;
  - при `401` автоматически вызывает `/auth/refresh`;
  - сохраняет новый access token и повторяет исходный запрос.
- Почему это подтверждает вашу работу:
  - показывает интеграцию frontend и backend на уровне авторизации;
  - демонстрирует не просто запросы к API, а полноценную обработку сессии и восстановление авторизации;
  - это хороший пример прикладной инфраструктуры приложения.
- Что вставлять в отчёт:
  - сокращённую выдержку;
  - достаточно показать создание клиента и `response interceptor`.

```ts
export const apiClient = axios.create({
    baseURL,
    withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
    const token = getAccessToken();

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (!error.response || error.response.status !== 401 || originalRequest._retry) {
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        const refreshResponse = await axios.post(`${baseURL}/auth/refresh`, undefined, {
            withCredentials: true,
        });

        setAuthSession(refreshResponse.data);
        originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.access_token}`;

        return apiClient(originalRequest);
    }
);
```

### 2. React Query hook для загрузки данных

- Путь к файлу: `apps/frontend/src/entities/pet/model/pet.queries.ts`
- Что делает код:
  - определяет `queryKey` для питомцев, пород и фото;
  - загружает список питомцев через `useQuery`;
  - задаёт `staleTime`, чтобы не делать лишние запросы.
- Почему это подтверждает вашу работу:
  - показывает, что на frontend организован нормальный data layer;
  - доказывает использование React Query не только для запроса, но и для структурирования кеша.
- Что вставлять в отчёт:
  - сокращённую выдержку;
  - лучше показать `petQueryKeys` и один конкретный хук, например `usePetsQuery`.

```ts
export const petQueryKeys = {
    all: ["pets"] as const,
    list: () => [...petQueryKeys.all, "list"] as const,
    breeds: () => [...petQueryKeys.all, "breeds"] as const,
    photo: (petId: number) => [...petQueryKeys.all, "photo", petId] as const,
};

export function usePetsQuery() {
    return useQuery({
        queryKey: petQueryKeys.list(),
        queryFn: getPets,
        staleTime: 60_000,
    });
}
```

### 3. Mutation hook с `invalidateQueries` и загрузкой файла через presigned URL

- Пути к файлам:
  - `apps/frontend/src/features/upload-document/model/use-upload-document.ts`
  - `apps/frontend/src/entities/document/api/document.api.ts`
- Что делает код:
  - запрашивает у backend presigned upload URL;
  - загружает файл напрямую в storage через `fetch`;
  - подтверждает загрузку на backend;
  - после успеха инвалидирует кеш списка документов.
- Почему это подтверждает вашу работу:
  - это один из самых сильных примеров сквозной интеграции frontend, backend и object storage;
  - показывает и mutation, и `invalidateQueries`, и работу с файлами.
- Что вставлять в отчёт:
  - сокращённую выдержку;
  - хорошо смотрится один фрагмент из `use-upload-document.ts` и короткий кусок `uploadDocumentFile(...)`.

```ts
return useMutation({
    mutationFn: async ({ petId, file, documentTypeId, customName }) => {
        const uploadUrlResponse = await createPetDocumentUploadUrl(petId, {
            document_type_id: documentTypeId,
            content_type: file.type || "application/octet-stream",
            custom_name: customName?.trim() || undefined,
        });

        await uploadDocumentFile(uploadUrlResponse.upload_url, file);

        return completePetDocumentUpload(petId, {
            document_type_id: documentTypeId,
            object_key: uploadUrlResponse.object_key,
            custom_name: uploadUrlResponse.custom_name,
        });
    },

    onSuccess: (_createdDocument, variables) => {
        void queryClient.invalidateQueries({
            queryKey: ["documents", "list", variables.petId],
        });
    },
});
```

```ts
export async function uploadDocumentFile(uploadUrl: string, file: File): Promise<void> {
    const response = await fetch(uploadUrl, {
        method: "PUT",
        headers: {
            "Content-Type": file.type || "application/octet-stream",
        },
        body: file,
    });

    if (!response.ok) {
        throw new Error("Failed to upload document file");
    }
}
```

### 4. Форма с React Hook Form + Zod

- Путь к файлу: `apps/frontend/src/features/auth/ui/login-form.tsx`
- Что делает код:
  - создаёт форму логина через `useForm`;
  - подключает `zodResolver(loginSchema)`;
  - валидирует ввод;
  - показывает ошибки и отправляет mutation.
- Почему это подтверждает вашу работу:
  - показывает, что формы в проекте построены на современном стеке;
  - подтверждает наличие клиентской валидации, связанной с API-логикой.
- Что вставлять в отчёт:
  - сокращённую выдержку;
  - лучше брать только инициализацию `useForm` и `onSubmit`.

```tsx
const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
} = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
        email: "",
        password: "",
    },
    mode: "onBlur",
});

const onSubmit = async (values: LoginFormValues) => {
    try {
        await loginMutation.mutate(values);
    } catch {
        setError("root", {
            message: "Неверный логин или пароль",
        });
    }
};
```

### 5. Backend endpoint + service layer с бизнес-логикой и обработкой ошибки

- Пути к файлам:
  - `apps/backend/src/api/pet_documents.py`
  - `apps/backend/src/service/pet_documents.py`
- Что делает код:
  - endpoint принимает запрос на удаление документа питомца;
  - service проверяет владельца, удаляет запись из БД, затем удаляет файл из storage;
  - если удаление файла падает, сервис пытается восстановить состояние БД и возвращает `AppError`.
- Почему это подтверждает вашу работу:
  - показывает полноценную backend-цепочку;
  - особенно хорошо демонстрирует бизнес-логику, а не только CRUD;
  - это ещё и сильный пример обработки ошибки и отката изменений.
- Что вставлять в отчёт:
  - сокращённую выдержку;
  - лучше показать короткий endpoint и основную часть метода `delete(...)`.

```py
@pet_documents_router.delete("/{document_row_id}")
async def delete_document(
    pet_id: int,
    document_row_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await pet_documents_service.delete(db, pet_id, document_row_id, current_user_id)
    return {"deleted": True}
```

```py
async def delete(self, db: AsyncSession, pet_id: int, document_row_id: int, user_id: int) -> None:
    await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
    doc = await self.get_one(db, pet_id, document_row_id, user_id)
    object_key = doc.object_key

    await db.delete(doc)
    await db.commit()

    try:
        await self.storage_service.delete_object(object_key)
    except Exception as exc:
        db.add(PetDocument(**snapshot))
        await db.commit()
        raise AppError(
            "Failed to delete document file from storage; changes were rolled back",
            status_code=500,
        ) from exc
```

## Дополнительные кандидаты по категориям

Если в отчёте понадобится не 5, а другой набор примеров, ниже собран удобный каталог по вашим категориям.

| Категория | Файл | Что показывает | Что лучше вставлять |
|---|---|---|---|
| Route guard для защищённых маршрутов | `apps/frontend/src/app/router/guards.tsx` | редирект неавторизованного пользователя на страницу входа | короткую выдержку |
| Компонент карточки питомца | `apps/frontend/src/widgets/pet-card/pet-card.tsx` | UI-компонент, который получает данные питомца и подгружает фото | сокращённую выдержку |
| Backend endpoint для сущности | `apps/backend/src/api/pet_documents.py` | REST-слой для документов питомца | короткую выдержку одного endpoint |
| Service layer метод с бизнес-логикой | `apps/backend/src/service/pet_documents.py` | проверка прав, работа с БД и storage, откат при ошибке | сокращённую выдержку |
| Repository method для работы с БД | `apps/backend/src/repositories/sharing.py` | SQLAlchemy-запросы через `select/join/where` | короткую выдержку |
| SQLAlchemy model | `apps/backend/src/models/PetDocument.py` | описание таблицы `pet_documents` и её полей | короткую выдержку |
| Alembic migration | `apps/backend/alembic/versions/7e2f4a1c9b3d_expand_animal_breed_length_to_100.py` | изменение схемы БД через миграцию | полный короткий фрагмент |
| Пример обработки ошибки | `apps/backend/src/service/pet_documents.py` | `AppError` и откат состояния при неудачном удалении файла | сокращённую выдержку |

## Короткие запасные фрагменты

### Route guard

- Путь к файлу: `apps/frontend/src/app/router/guards.tsx`
- Почему полезен:
  - хорошо показывает защиту приватных экранов;
  - короткий и понятный для отчёта фрагмент.
- Что вставлять:
  - полный фрагмент, он очень маленький.

```ts
export function ensureAuth() {
    const authStatus = getAuthStatus();

    if (authStatus !== "authenticated") {
        throw redirect({
            to: appRoutes.login,
        });
    }
}
```

### Компонент карточки питомца

- Путь к файлу: `apps/frontend/src/widgets/pet-card/pet-card.tsx`
- Почему полезен:
  - подтверждает, что вы собирали пользовательский интерфейс, а не только инфраструктуру;
  - показывает связку данных, роутинга и отображения.
- Что вставлять:
  - сокращённую выдержку.

```tsx
export function PetCard({ pet }: PetCardProps) {
    const photoQuery = usePetPhotoQuery(pet.id, Boolean(pet.photoObjectKey));

    return (
        <Link
            className="pet-card"
            to={appRoutes.petProfile}
            params={{ petId: String(pet.id) }}
        >
            {photoQuery.data ? (
                <img src={photoQuery.data} alt={pet.name} className="pet-image" />
            ) : (
                <div className="pet-image pet-image-placeholder">
                    {pet.name.slice(0, 1).toUpperCase()}
                </div>
            )}
        </Link>
    );
}
```

### Repository method для работы с БД

- Путь к файлу: `apps/backend/src/repositories/sharing.py`
- Почему полезен:
  - показывает слой доступа к данным отдельно от business logic;
  - видно, что вы работали с `select`, `join` и фильтрацией.
- Что вставлять:
  - сокращённую выдержку метода `get_shared_users(...)`.

```py
async def get_shared_users(self, db: AsyncSession, pet_id: int) -> List[SharedUser]:
    res = await db.execute(
        select(SharedUser, UserInfo)
        .join(UserInfo, UserInfo.id == SharedUser.shared_user_id)
        .where(*active_shared_access_clause(pet_id=pet_id))
    )
    return res.all()
```

### SQLAlchemy model

- Путь к файлу: `apps/backend/src/models/PetDocument.py`
- Почему полезен:
  - наглядно показывает структуру одной сущности и поля для хранения документов;
  - хорошо подходит как пример ORM-модели.
- Что вставлять:
  - сокращённую выдержку.

```py
class PetDocument(Base):
    __tablename__ = "pet_documents"

    id: Mapped[int_primary_key]
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets_info.id", ondelete="CASCADE"))
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents_types.id", ondelete="CASCADE"))
    custom_name: Mapped[str] = mapped_column(String(255))
    object_key: Mapped[str] = mapped_column(Text, unique=True)
```

### Alembic migration

- Путь к файлу: `apps/backend/alembic/versions/7e2f4a1c9b3d_expand_animal_breed_length_to_100.py`
- Почему полезен:
  - показывает, что вы меняли схему БД осознанно и через миграции;
  - особенно удобно, если в отчёте нужно упомянуть развитие модели данных.
- Что вставлять:
  - полный короткий фрагмент.

```py
def upgrade() -> None:
    op.alter_column(
        'animals_breeds',
        'animal_breed',
        existing_type=sa.String(length=50),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
```

## Что я бы рекомендовал вставить именно в итоговый отчёт

Если вам нужно оставить только 5 примеров, я бы взял именно такой набор:

1. `apps/frontend/src/shared/api/client.ts`
   Показывает интеграцию frontend/backend и refresh-auth flow.
2. `apps/frontend/src/entities/pet/model/pet.queries.ts`
   Показывает data layer и React Query.
3. `apps/frontend/src/features/upload-document/model/use-upload-document.ts`
   Показывает mutation, invalidation и загрузку файлов.
4. `apps/frontend/src/features/auth/ui/login-form.tsx`
   Показывает форму, валидацию и работу с пользователем.
5. `apps/backend/src/service/pet_documents.py`
   Показывает реальную backend-логику, а не только routing.

Такой набор выглядит сбалансированно: 3 frontend-примера, 1 интеграционный, 1 backend-пример с бизнес-логикой.

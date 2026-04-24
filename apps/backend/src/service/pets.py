from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import PetAccessDeniedError, PetNotFoundError, PetOwnerOnlyError
from src.models import PetInfo, SharedUser
from src.schemas import PetCreate, PetResponse, UpdatePet
from src.service.storage import StorageService
from src.repositories import PetsRepository
from src.sharing_active import active_shared_access_clause


@dataclass(frozen=True, slots=True)
class PetPhotoSnapshot:
    object_key: str
    content_type: str | None
    size_bytes: int | None
    etag: str | None
    uploaded_at: datetime | None

class PetsService:
    def __init__(self):
        self.repo = PetsRepository()

    SIMPLE_UPDATE_FIELDS = {
        "pet_name": "pet_name",
        "pet_date_of_birth": "pet_date_of_birth",
        "animal_type_id": "animal_type_id",
        "animal_breed_id": "animal_breed_id",
        "pedigree": "pedigree",
        "pet_length": "pet_length",
        "pet_neck_girth": "pet_neck_girth",
        "pet_breast_girth": "pet_breast_girth",
        "pet_weight": "pet_weight",
        "pet_is_sterylyzed": "pet_is_sterylyzed",
    }
    PHOTO_METADATA_FIELDS = (
        "pet_photo_content_type",
        "pet_photo_size_bytes",
        "pet_photo_etag",
        "pet_photo_uploaded_at",
    )

    @staticmethod
    def photo_snapshot(pet: PetInfo) -> PetPhotoSnapshot | None:
        if not pet.pet_photo_object_key:
            return None
        return PetPhotoSnapshot(
            object_key=pet.pet_photo_object_key,
            content_type=pet.pet_photo_content_type,
            size_bytes=pet.pet_photo_size_bytes,
            etag=pet.pet_photo_etag,
            uploaded_at=pet.pet_photo_uploaded_at,
        )

    def to_response(self, pet: PetInfo, current_user_id: int) -> PetResponse:
        return PetResponse(
            id=pet.id,
            user_id=pet.user_id,
            pet_name=pet.pet_name,
            pet_date_of_birth=pet.pet_date_of_birth,
            animal_type_id=pet.animal_type_id,
            animal_breed_id=pet.animal_breed_id,
            pedigree=bool(pet.pedigree),
            pet_length=float(pet.pet_length),
            pet_neck_girth=float(pet.pet_neck_girth),
            pet_breast_girth=float(pet.pet_breast_girth),
            pet_weight=float(pet.pet_weight),
            pet_is_sterylyzed=pet.pet_is_sterylyzed,
            pet_photo_object_key=pet.pet_photo_object_key,
            pet_photo_content_type=pet.pet_photo_content_type,
            pet_photo_size_bytes=pet.pet_photo_size_bytes,
            pet_photo_etag=pet.pet_photo_etag,
            pet_photo_uploaded_at=pet.pet_photo_uploaded_at,
            is_shared=pet.user_id != current_user_id,
        )

    def _build_pet(self, payload: PetCreate, user_id: int) -> PetInfo:
        return PetInfo(
            pet_name=payload.pet_name.strip(),
            animal_type_id=payload.animal_type_id,
            pet_date_of_birth=payload.pet_date_of_birth,
            user_id=user_id,
            animal_breed_id=payload.animal_breed_id,
            pedigree=payload.pedigree,
            pet_neck_girth=payload.pet_neck_girth,
            pet_breast_girth=payload.pet_breast_girth,
            pet_length=payload.pet_length,
            pet_weight=payload.pet_weight,
            pet_is_sterylyzed=payload.pet_is_sterylyzed,
            pet_photo_object_key=payload.pet_photo_object_key,
            pet_photo_content_type=payload.pet_photo_content_type,
            pet_photo_size_bytes=payload.pet_photo_size_bytes,
            pet_photo_etag=payload.pet_photo_etag,
            pet_photo_uploaded_at=payload.pet_photo_uploaded_at,
        )

    async def create_pet(self, db: AsyncSession, payload: PetCreate, user_id: int) -> PetInfo | None:
        pet = self._build_pet(payload, user_id)
        db.add(pet)

        await db.commit()
        await db.refresh(pet)
        return pet

    async def create_pet_with_optional_photo(
        self,
        db: AsyncSession,
        payload: PetCreate,
        user_id: int,
        *,
        photo_bytes: bytes | None = None,
        photo_content_type: str | None = None,
        storage_service: StorageService | None = None,
    ) -> PetResponse:
        storage = storage_service or StorageService()
        pet = self._build_pet(payload, user_id)
        uploaded_object_key: str | None = None

        db.add(pet)
        try:
            await db.flush()

            if photo_bytes is not None and photo_content_type is not None:
                uploaded_object_key = storage.build_pet_photo_object_key(
                    user_id=user_id,
                    pet_id=pet.id,
                    content_type=photo_content_type,
                )
                put_result = await storage.upload_bytes(
                    object_key=uploaded_object_key,
                    payload=photo_bytes,
                    content_type=photo_content_type,
                )
                etag_raw = put_result.get("ETag")
                pet.pet_photo_object_key = uploaded_object_key
                pet.pet_photo_content_type = photo_content_type
                pet.pet_photo_size_bytes = len(photo_bytes)
                pet.pet_photo_etag = str(etag_raw).strip('"') if etag_raw is not None else None
                pet.pet_photo_uploaded_at = storage.now_utc()

            await db.commit()
            await db.refresh(pet)
        except Exception:
            await db.rollback()
            await storage.delete_object_quietly(uploaded_object_key)
            raise

        return self.to_response(pet, user_id)

    async def list_all_pets(
        self,
        db: AsyncSession,
        user_id: int,
        offset: int = 0,
        limit: int = 50,
    ) -> list[PetResponse]:
        owned_result = await db.execute(
            select(PetInfo)
            .where(PetInfo.user_id == user_id)
        )
        shared_result = await db.execute(
            select(PetInfo)
            .join(SharedUser, SharedUser.shared_pet_id == PetInfo.id)
            .where(
                and_(
                    SharedUser.shared_pet_id == PetInfo.id,
                    *active_shared_access_clause(user_id),
                )
            )
        )

        pets_by_id: dict[int, PetInfo] = {}
        for pet in list(owned_result.scalars().all()) + list(shared_result.scalars().all()):
            pets_by_id[pet.id] = pet

        pets = list(pets_by_id.values())
        pets.sort(key=lambda pet: pet.id)
        pets = pets[offset: offset + limit]
        return [self.to_response(pet, user_id) for pet in pets]

    async def get_pet_by_id(self, db: AsyncSession, pet_id: int) -> PetInfo | None:
        return await self.repo.get_by_id(db, pet_id)

    async def get_pet_for_user(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
        allow_shared: bool = True,
    ) -> PetResponse:
        pet = await self.get_pet_by_id(db, pet_id)
        if not pet:
            raise PetNotFoundError()

        if pet.user_id == user_id:
            return self.to_response(pet, user_id)

        if allow_shared:
            shared_access = await db.execute(
                select(SharedUser).where(*active_shared_access_clause(user_id, pet_id))
            )
            if shared_access.scalar_one_or_none():
                return self.to_response(pet, user_id)

        raise PetAccessDeniedError()

    async def ensure_pet_owner(self, db: AsyncSession, pet_id: int, user_id: int) -> PetInfo:
        pet = await self.repo.get_by_id(db, pet_id)
        if not pet:
            raise PetNotFoundError()
        if pet.user_id != user_id:
            raise PetOwnerOnlyError()
        return pet

    async def update_pet(self, db: AsyncSession, pet_id: int, payload: UpdatePet, user_id: int):
        pet = await self.ensure_pet_owner(db, pet_id, user_id)
        
        data = payload.model_dump(exclude_unset=True)
        self._apply_simple_updates(pet, data)
        self._apply_photo_updates(pet, data)

        await db.commit()
        await db.refresh(pet)
        return self.to_response(pet, user_id)

    def _apply_simple_updates(self, pet: PetInfo, data: dict[str, object]) -> None:
        for payload_field, model_field in self.SIMPLE_UPDATE_FIELDS.items():
            value = data.get(payload_field)
            if value is None:
                continue
            if payload_field == "pet_name":
                value = str(value).strip()
            setattr(pet, model_field, value)

    def _apply_photo_updates(self, pet: PetInfo, data: dict[str, object]) -> None:
        if "pet_photo_object_key" in data:
            pet.pet_photo_object_key = data["pet_photo_object_key"]
            for field_name in self.PHOTO_METADATA_FIELDS:
                if field_name not in data:
                    setattr(pet, field_name, None)

        for field_name in self.PHOTO_METADATA_FIELDS:
            if field_name in data:
                setattr(pet, field_name, data[field_name])

    async def delete_pet(self, db: AsyncSession, pet_id: int, user_id: int) -> bool:
        pet = await self.ensure_pet_owner(db, pet_id, user_id)

        await db.delete(pet)
        await db.commit()
        return True

    async def list_pet_object_keys_for_cleanup(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
    ) -> list[str]:
        pet = await self.ensure_pet_owner(db, pet_id, user_id)
        object_keys = await self.repo.get_docs_keys(db, pet_id)
        if pet.pet_photo_object_key:
            object_keys.append(pet.pet_photo_object_key)
        return object_keys

    async def set_pet_photo_metadata(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
        *,
        object_key: str,
        content_type: str | None,
        size_bytes: int | None,
        etag: str | None,
        uploaded_at: datetime | None,
    ) -> PetResponse:
        pet = await self.ensure_pet_owner(db, pet_id, user_id)
        pet.pet_photo_object_key = object_key
        pet.pet_photo_content_type = content_type
        pet.pet_photo_size_bytes = size_bytes
        pet.pet_photo_etag = etag
        pet.pet_photo_uploaded_at = uploaded_at
        await db.commit()
        await db.refresh(pet)
        return self.to_response(pet, user_id)

    async def restore_pet_photo(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
        snapshot: PetPhotoSnapshot | None,
    ) -> PetResponse | None:
        if snapshot is None:
            return await self.clear_pet_photo(db, pet_id, user_id)

        return await self.set_pet_photo_metadata(
            db,
            pet_id,
            user_id,
            object_key=snapshot.object_key,
            content_type=snapshot.content_type,
            size_bytes=snapshot.size_bytes,
            etag=snapshot.etag,
            uploaded_at=snapshot.uploaded_at,
        )

    async def clear_pet_photo(self, db: AsyncSession, pet_id: int, user_id: int) -> str | None:
        pet = await self.ensure_pet_owner(db, pet_id, user_id)
        previous_key = pet.pet_photo_object_key
        pet.pet_photo_object_key = None
        pet.pet_photo_content_type = None
        pet.pet_photo_size_bytes = None
        pet.pet_photo_etag = None
        pet.pet_photo_uploaded_at = None
        await db.commit()
        return previous_key or None

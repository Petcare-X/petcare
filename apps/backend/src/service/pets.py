from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import PetAccessDeniedError, PetNotFoundError, PetOwnerOnlyError
from src.models import PetInfo, SharedUser
from src.schemas import PetCreate, PetResponse, UpdatePet


@dataclass(frozen=True, slots=True)
class PetPhotoSnapshot:
    object_key: str
    content_type: str | None
    size_bytes: int | None
    etag: str | None
    uploaded_at: datetime | None


def active_shared_access_clause(
    shared_user_id: int | None = None,
    pet_id: int | None = None,
):
    conditions = [
        or_(
            SharedUser.sharing_end.is_(None),
            SharedUser.sharing_end > datetime.now(timezone.utc),
        ),
    ]
    if shared_user_id is not None:
        conditions.append(SharedUser.shared_user_id == shared_user_id)
    if pet_id is not None:
        conditions.append(SharedUser.shared_pet_id == pet_id)
    return conditions

class PetsService:
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

    async def create_pet(self, db: AsyncSession, payload: PetCreate, user_id: int) -> PetInfo | None:
        pet = PetInfo(
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

        db.add(pet)

        await db.commit()
        await db.refresh(pet)
        return pet

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
        return await db.get(PetInfo, pet_id)

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
        pet = await self.get_pet_by_id(db, pet_id)
        if not pet:
            raise PetNotFoundError()
        if pet.user_id != user_id:
            raise PetOwnerOnlyError()
        return pet

    async def update_pet(self, db: AsyncSession, pet_id: int, payload: UpdatePet, user_id: int):
        pet = await self.ensure_pet_owner(db, pet_id, user_id)
        
        data = payload.model_dump(exclude_unset=True)

        if "pet_name" in data and data["pet_name"] is not None:
            pet.pet_name = data["pet_name"].strip()

        if "pet_date_of_birth" in data and data["pet_date_of_birth"] is not None:
            pet.pet_date_of_birth = data["pet_date_of_birth"]

        if "animal_type_id" in data and data["animal_type_id"] is not None:
            pet.animal_type_id = data["animal_type_id"]
            
        if "animal_breed_id" in data and data["animal_breed_id"] is not None:
            pet.animal_breed_id = data["animal_breed_id"]

        if "pedigree" in data and data["pedigree"] is not None:
            pet.pedigree = data["pedigree"]

        if "pet_length" in data and data["pet_length"] is not None:
            pet.pet_length = data["pet_length"]

        if "pet_neck_girth" in data and data["pet_neck_girth"] is not None:
            pet.pet_neck_girth = data["pet_neck_girth"]

        if "pet_breast_girth" in data and data["pet_breast_girth"] is not None:
            pet.pet_breast_girth = data["pet_breast_girth"]

        if "pet_weight" in data and data["pet_weight"] is not None:
            pet.pet_weight = data["pet_weight"]

        if "pet_is_sterylyzed" in data and data["pet_is_sterylyzed"] is not None:
            pet.pet_is_sterylyzed = data["pet_is_sterylyzed"]

        if "pet_photo_object_key" in data and data["pet_photo_object_key"] is not None:
            pet.pet_photo_object_key = data["pet_photo_object_key"]
            if "pet_photo_content_type" not in data:
                pet.pet_photo_content_type = None
            if "pet_photo_size_bytes" not in data:
                pet.pet_photo_size_bytes = None
            if "pet_photo_etag" not in data:
                pet.pet_photo_etag = None
            if "pet_photo_uploaded_at" not in data:
                pet.pet_photo_uploaded_at = None

        if "pet_photo_content_type" in data:
            pet.pet_photo_content_type = data["pet_photo_content_type"]

        if "pet_photo_size_bytes" in data:
            pet.pet_photo_size_bytes = data["pet_photo_size_bytes"]

        if "pet_photo_etag" in data:
            pet.pet_photo_etag = data["pet_photo_etag"]

        if "pet_photo_uploaded_at" in data:
            pet.pet_photo_uploaded_at = data["pet_photo_uploaded_at"]

        await db.commit()
        await db.refresh(pet)
        return self.to_response(pet, user_id)

    async def delete_pet(self, db: AsyncSession, pet_id: int, user_id: int) -> bool:
        pet = await self.ensure_pet_owner(db, pet_id, user_id)

        await db.delete(pet)
        await db.commit()
        return True

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
        pet.pet_photo_object_key = ""
        pet.pet_photo_content_type = None
        pet.pet_photo_size_bytes = None
        pet.pet_photo_etag = None
        pet.pet_photo_uploaded_at = None
        await db.commit()
        return previous_key or None

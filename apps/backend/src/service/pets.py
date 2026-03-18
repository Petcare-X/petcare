from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import PetAccessDeniedError, PetNotFoundError, PetOwnerOnlyError
from src.models import PetInfo, SharedUser
from src.schemas import PetCreate, PetResponse, UpdatePet


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
    def to_response(self, pet: PetInfo, current_user_id: int) -> PetResponse:
        return PetResponse(
            id=pet.id,
            owner_user_id=pet.user_id,
            pet_name=pet.pet_name,
            date_of_birth=pet.pet_date_of_birth,
            type=pet.pet_type,
            breed=pet.pet_breed,
            pedigree=bool(pet.pet_pedigree) if pet.pet_pedigree is not None else None,
            length=float(pet.pet_length) if pet.pet_length is not None else None,
            neck_girth=float(pet.pet_neck_girth) if pet.pet_neck_girth is not None else None,
            breast_girth=float(pet.pet_breast_girth) if pet.pet_breast_girth is not None else None,
            is_sterylized=pet.pet_is_sterylyzed,
            photo_url=pet.pet_photo,
            is_shared=pet.user_id != current_user_id,
        )

    async def create_pet(self, db: AsyncSession, payload: PetCreate, user_id: int) -> PetInfo | None:
        pet = PetInfo(
            pet_name=payload.pet_name.strip(),
            pet_type=payload.type,
            pet_date_of_birth=payload.date_of_birth,
            user_id=user_id,
            pet_breed=payload.breed,
            pet_pedigree=payload.pedigree,
            pet_neck_girth=payload.neck_girth,
            pet_breast_girth=payload.neck_girth,
            pet_length=payload.length,
            pet_is_sterylyzed=payload.is_sterylized,
            pet_photo=payload.photo_url
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

        if "date_of_birth" in data and data["date_of_birth"] is not None:
            pet.pet_date_of_birth = data["date_of_birth"]

        if "type" in data and data["type"] is not None:
            pet.pet_type = data["type"]
            
        if "breed" in data and data["breed"] is not None:
            pet.pet_breed = data["breed"]

        if "pedigree" in data and data["pedigree"] is not None:
            pet.pet_pedigree = data["pedigree"]

        if "length" in data and data["length"] is not None:
            pet.pet_length = data["length"]

        if "neck_girth" in data and data["neck_girth"] is not None:
            pet.pet_neck_girth = data["neck_girth"]

        if "breast_girth" in data and data["breast_girth"] is not None:
            pet.pet_breast_girth = data["breast_girth"]

        if "is_sterylized" in data and data["is_sterylized"] is not None:
            pet.pet_is_sterylyzed = data["is_sterylized"]

        if "photo_url" in data and data["photo_url"] is not None:
            pet.pet_photo = data["photo_url"]

        await db.commit()
        await db.refresh(pet)
        return self.to_response(pet, user_id)

    async def delete_pet(self, db: AsyncSession, pet_id: int, user_id: int) -> bool:
        pet = await self.ensure_pet_owner(db, pet_id, user_id)

        await db.delete(pet)
        await db.commit()
        return True

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import PetInfo
from src.schemas import CreatePet, UpdatePet

class PetsService:
    async def create_pet(self, db: AsyncSession, payload: CreatePet) -> PetInfo | None:
        pet = PetInfo(
            pet_name=payload.pet_name.strip(),
            pet_type=payload.type,
            pet_date_of_birth=payload.date_of_birth,
            user_id=payload.user_id,
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

    async def list_all_pets(self, db: AsyncSession, offset: int = 0, limit: int = 50) -> list[PetInfo]:
        pet = await db.execute(select(PetInfo).offset(offset).limit(limit))
        return list(pet.scalars().all())

    async def get_pet_by_id(self, db: AsyncSession, pet_id: int) -> PetInfo | None:
        return await db.get(PetInfo, pet_id)

    async def update_pet(self, db: AsyncSession, pet_id: int, payload: UpdatePet):
        pet = await self.get_pet_by_id(db, pet_id)
        if not pet:
            return None
        
        data = payload.model_dump(exclude_unset=True)

        if "date_of_birth" in data and data["date_of_birth"] is not None:
            pet.pet_date_of_birth = data["date_of_birth"]
            
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

        await db.commit()
        await db.refresh(pet)
        return pet

    async def delete_pet(self, db: AsyncSession, pet_id: int) -> bool:
        pet = await self.get_pet_by_id(db, pet_id)
        if not pet:
            return False

        await db.delete(pet)
        await db.commit()
        return True
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AnimalBreed, AnimalType
from src.schemas.animals import AnimalBreedResponse, AnimalTypeResponse


class AnimalsService:
    async def list_animal_types(self, db: AsyncSession) -> list[AnimalTypeResponse]:
        result = await db.execute(select(AnimalType).order_by(AnimalType.id))
        return [
            AnimalTypeResponse(id=animal_type.id, animal_name=animal_type.animal_name)
            for animal_type in result.scalars().all()
        ]

    async def list_breeds_for_type(
        self,
        db: AsyncSession,
        animal_type_id: int,
    ) -> list[AnimalBreedResponse]:
        result = await db.execute(
            select(AnimalBreed)
            .where(AnimalBreed.animal_type_id == animal_type_id)
            .order_by(AnimalBreed.id)
        )
        return [
            AnimalBreedResponse(
                id=breed.id,
                animal_breed=breed.animal_breed,
                animal_type_id=breed.animal_type_id,
            )
            for breed in result.scalars().all()
        ]

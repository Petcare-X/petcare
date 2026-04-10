from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.schemas.animals import AnimalBreedResponse, AnimalTypeResponse
from src.service.animals import AnimalsService


animal_types_router = APIRouter(prefix="/animal-types", tags=["animal-types"])

animals_service = AnimalsService()


@animal_types_router.get("", response_model=list[AnimalTypeResponse])
async def list_animal_types(
    db: AsyncSession = Depends(get_db),
):
    return await animals_service.list_animal_types(db)


@animal_types_router.get("/{animal_type_id}/breeds", response_model=list[AnimalBreedResponse])
async def list_animal_breeds(
    animal_type_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await animals_service.list_breeds_for_type(db, animal_type_id)

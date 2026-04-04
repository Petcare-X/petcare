from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.pet_documents import pet_documents_router
from src.api.pet_photos import pet_photos_router
from src.api.sharing import pet_shares_router
from src.core.db import get_db
from src.core.security import get_current_user_id
from src.schemas.pets import (
    PetCreate,
    PetResponse,
    UpdatePet,
)
from src.service import PetsService

pets_router = APIRouter(prefix="/pets")

pets_service = PetsService()

pets_router.include_router(pet_photos_router, prefix="/{pet_id}")
pets_router.include_router(pet_documents_router, prefix="/{pet_id}")
pets_router.include_router(pet_shares_router, prefix="/{pet_id}")


@pets_router.post("", status_code=201, response_model=PetResponse, tags=["pets"])
async def create(
    payload: PetCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    pet = await pets_service.create_pet(db, payload, current_user_id)
    return pets_service.to_response(pet, current_user_id)


@pets_router.get("", response_model=list[PetResponse], tags=["pets"])
async def list_(
    db: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 50,
    current_user_id: int = Depends(get_current_user_id),
):
    return await pets_service.list_all_pets(db, current_user_id, offset, limit)


@pets_router.patch("/{pet_id}", response_model=PetResponse, tags=["pets"])
async def patch_data(
    pet_id: int,
    payload: UpdatePet,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    pet = await pets_service.update_pet(db, pet_id, payload, current_user_id)
    return pet


@pets_router.delete("/{pet_id}", tags=["pets"])
async def remove(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await pets_service.delete_pet(db, pet_id, current_user_id)
    return {"deleted": True}


@pets_router.get("/{pet_id}", response_model=PetResponse, tags=["pets"])
async def get(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await pets_service.get_pet_for_user(db, pet_id, current_user_id)

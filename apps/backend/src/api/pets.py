from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user_id
from src.core.db import get_db
from src.service import PetsService, SharingService

from src.schemas.pets import PetCreate, PetResponse, UpdatePet

pets_router = APIRouter(prefix="/pets", tags=["pets"])

pets_service = PetsService()
sharing_service = SharingService()

@pets_router.post("", status_code=201, response_model=PetResponse)
async def create(
    payload: PetCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    pet = await pets_service.create_pet(db, payload, current_user_id)
    return pets_service.to_response(pet, current_user_id)

@pets_router.get("", response_model=list[PetResponse])
async def list_(
    db: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 50,
    current_user_id: int = Depends(get_current_user_id),
):
    return await pets_service.list_all_pets(db, current_user_id, offset, limit)


@pets_router.patch("/{pet_id}", response_model=PetResponse)
async def patch_data(
    pet_id: int,
    payload: UpdatePet,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    pet = await pets_service.update_pet(db, pet_id, payload, current_user_id)
    return pet


@pets_router.delete("/{pet_id}")
async def remove(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    ok = await pets_service.delete_pet(db, pet_id, current_user_id)
    return {"deleted": True}

@pets_router.get("/{pet_id}", response_model=PetResponse)
async def get(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await pets_service.get_pet_for_user(db, pet_id, current_user_id)


@pets_router.get("/{pet_id}/shared-users",
                status_code=200,
                description="FOR TEST")
async def get_shared_users(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await sharing_service.get_shared_users(db, pet_id, current_user_id)


@pets_router.delete("/{pet_id}/access/{user_id}",
                    status_code=200,
                    description="FOR TEST")
async def remove_access(
    pet_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await sharing_service.revoke_access(db, current_user_id, pet_id, user_id)

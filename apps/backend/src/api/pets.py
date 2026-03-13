from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.service import PetsService, SharingService

from src.schemas.pets import CreatePet, UpdatePet

pets_router = APIRouter(prefix="/pets", tags=["pets"])

pets_service = PetsService()
sharing_service = SharingService()

@pets_router.post("")
async def create(payload: CreatePet, db: AsyncSession = Depends(get_db)):
    try:
        pet = await pets_service.create_pet(db, payload)
        if pet:
            return {"message": "Pet created succesfully", "pet": pet}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@pets_router.get("/{pet_id}")
async def get(pet_id: int, db: AsyncSession = Depends(get_db)):
    pet = await pets_service.get_pet_by_id(db, pet_id)
    if not pet:
        raise HTTPException(404, "pet not found")
    return pet


@pets_router.get("")
async def list_(db: AsyncSession = Depends(get_db), offset: int = 0, limit: int = 50):
    return await pets_service.list_all_pets(db, offset, limit)


@pets_router.patch("/{pet_id}/data")
async def patch_data(pet_id: int, payload: UpdatePet, db: AsyncSession = Depends(get_db)):
    try:
        pet = await pets_service.update_pet(db, pet_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not pet:
        raise HTTPException(404, "Pet not found")
    return pet


@pets_router.delete("/{pet_id}")
async def remove(pet_id: int, db: AsyncSession = Depends(get_db)):
    ok = await pets_service.delete_pet(db, pet_id)
    if not ok:
        raise HTTPException(404, "Pet not found")
    return {"deleted": True}


@pets_router.get("/shared",
                status_code=200,
                description="FOR TEST")
async def list_shared_pets(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await sharing_service.get_shared_pets(db, user_id)
    if not result:
        raise HTTPException(404, "No shared pets found")
    return result


@pets_router.get("/{pet_id}/shared-users",
                status_code=200,
                description="FOR TEST")
async def get_shared_users(pet_id: int, db: AsyncSession = Depends(get_db)):
    result = await sharing_service.get_shared_users(db, pet_id)
    if not result:
        raise HTTPException(404, "No shared users found")
    return result


@pets_router.delete("/{pet_id}/access/{user_id}",
                    status_code=200,
                    description="FOR TEST")
async def remove_access(pet_id: int, user_id: int):
    ok = await sharing_service.revoke_access(pet_id, user_id)
    if not ok:
        raise HTTPException(404, "Access not found")
    return {"deleted": True}
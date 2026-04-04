from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_db
from src.core.security import get_current_user_id
from src.exceptions import AppError
from src.schemas.pets import (
    PetPhotoCompleteRequest,
    PetPhotoDownloadUrlResponse,
    PetPhotoUploadUrlRequest,
    PetPhotoUploadUrlResponse,
    PetResponse,
)
from src.service import PetPhotoService, PetsService, StorageService


pet_photos_router = APIRouter(tags=["pet-photos"])

pet_photo_service = PetPhotoService()
pets_service = PetsService()
storage_service = StorageService()


@pet_photos_router.post(
    "/photo/upload-url",
    response_model=PetPhotoUploadUrlResponse,
)
async def get_photo_upload_url(
    pet_id: int,
    payload: PetPhotoUploadUrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await pet_photo_service.create_upload_url(
        db,
        pet_id=pet_id,
        user_id=current_user_id,
        content_type=payload.content_type,
    )


@pet_photos_router.post(
    "/photo/complete",
    response_model=PetResponse,
)
async def complete_photo_upload(
    pet_id: int,
    payload: PetPhotoCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await pet_photo_service.complete_upload(
        db,
        pet_id=pet_id,
        user_id=current_user_id,
        object_key=payload.object_key,
    )


@pet_photos_router.get(
    "/photo/download-url",
    response_model=PetPhotoDownloadUrlResponse,
)
async def get_photo_download_url(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    pet = await pets_service.get_pet_for_user(db, pet_id, current_user_id, allow_shared=True)
    if not pet.pet_photo_object_key:
        raise AppError("Pet photo is not set", status_code=404)
    download_url = await storage_service.create_download_url(pet.pet_photo_object_key)
    return PetPhotoDownloadUrlResponse(
        object_key=pet.pet_photo_object_key,
        download_url=download_url,
        expires_in=settings.MINIO_PRESIGNED_DOWNLOAD_TTL_SEC,
    )


@pet_photos_router.delete("/photo")
async def delete_photo(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await pet_photo_service.delete_photo(db, pet_id=pet_id, user_id=current_user_id)
    return {"deleted": True}

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import get_current_user_id
from src.core.db import get_db
from src.exceptions import AppError
from src.service import PetsService, SharingService, StorageService

from src.schemas.pets import (
    PetCreate,
    PetPhotoCompleteRequest,
    PetPhotoDownloadUrlResponse,
    PetPhotoUploadUrlRequest,
    PetPhotoUploadUrlResponse,
    PetResponse,
    UpdatePet,
)

pets_router = APIRouter(prefix="/pets", tags=["pets"])

pets_service = PetsService()
sharing_service = SharingService()
storage_service = StorageService()

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


@pets_router.post(
    "/{pet_id}/photo/upload-url",
    response_model=PetPhotoUploadUrlResponse,
)
async def get_photo_upload_url(
    pet_id: int,
    payload: PetPhotoUploadUrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await pets_service.ensure_pet_owner(db, pet_id, current_user_id)
    object_key = storage_service.build_pet_photo_object_key(
        user_id=current_user_id,
        pet_id=pet_id,
        content_type=payload.content_type,
    )
    upload_url = storage_service.create_upload_url(
        object_key=object_key,
        content_type=payload.content_type,
    )
    return PetPhotoUploadUrlResponse(
        object_key=object_key,
        upload_url=upload_url,
        expires_in=settings.MINIO_PRESIGNED_UPLOAD_TTL_SEC,
    )


@pets_router.post(
    "/{pet_id}/photo/complete",
    response_model=PetResponse,
)
async def complete_photo_upload(
    pet_id: int,
    payload: PetPhotoCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    allowed_prefix = f"users/{current_user_id}/pets/{pet_id}/photo/"
    if not payload.object_key.startswith(allowed_prefix):
        raise AppError("Object key does not belong to this pet", status_code=400)

    pet = await pets_service.ensure_pet_owner(db, pet_id, current_user_id)
    previous_key = pet.pet_photo_object_key or None

    head = storage_service.head_object(payload.object_key)
    content_type = head.get("ContentType")
    size_bytes_raw = head.get("ContentLength")
    etag_raw = head.get("ETag")
    size_bytes = int(size_bytes_raw) if isinstance(size_bytes_raw, int | float) else None
    etag = str(etag_raw).strip('"') if etag_raw is not None else None

    response = await pets_service.set_pet_photo_metadata(
        db,
        pet_id,
        current_user_id,
        object_key=payload.object_key,
        content_type=str(content_type) if content_type else None,
        size_bytes=size_bytes,
        etag=etag,
        uploaded_at=datetime.now(datetime.UTC),
    )

    if previous_key and previous_key != payload.object_key:
        storage_service.delete_object(previous_key)

    return response


@pets_router.get(
    "/{pet_id}/photo/download-url",
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
    download_url = storage_service.create_download_url(pet.pet_photo_object_key)
    return PetPhotoDownloadUrlResponse(
        object_key=pet.pet_photo_object_key,
        download_url=download_url,
        expires_in=settings.MINIO_PRESIGNED_DOWNLOAD_TTL_SEC,
    )


@pets_router.delete("/{pet_id}/photo")
async def delete_photo(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    previous_key = await pets_service.clear_pet_photo(db, pet_id, current_user_id)
    if previous_key:
        storage_service.delete_object(previous_key)
    return {"deleted": True}

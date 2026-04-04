from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.exceptions import AppError
from src.schemas.pets import PetPhotoUploadUrlResponse, PetResponse
from src.service.pets import PetsService
from src.service.storage import StorageService


class PetPhotoService:
    def __init__(self) -> None:
        self.pets_service = PetsService()
        self.storage_service = StorageService()

    async def _cleanup_uploaded_object(self, object_key: str | None) -> bool:
        return await self.storage_service.delete_object_quietly(object_key)

    async def create_upload_url(
        self,
        db: AsyncSession,
        *,
        pet_id: int,
        user_id: int,
        content_type: str,
    ) -> PetPhotoUploadUrlResponse:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        object_key = self.storage_service.build_pet_photo_object_key(
            user_id=user_id,
            pet_id=pet_id,
            content_type=content_type,
        )
        upload_url = await self.storage_service.create_upload_url(
            object_key=object_key,
            content_type=content_type,
        )
        return PetPhotoUploadUrlResponse(
            object_key=object_key,
            upload_url=upload_url,
            expires_in=settings.MINIO_PRESIGNED_UPLOAD_TTL_SEC,
        )

    async def complete_upload(
        self,
        db: AsyncSession,
        *,
        pet_id: int,
        user_id: int,
        object_key: str,
        uploaded_at: datetime | None = None,
    ) -> PetResponse:
        if not self.storage_service.is_pet_photo_key(object_key, user_id=user_id, pet_id=pet_id):
            raise AppError("Object key does not belong to this pet", status_code=400)

        pet = await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        previous_snapshot = self.pets_service.photo_snapshot(pet)
        previous_key = previous_snapshot.object_key if previous_snapshot else None
        metadata = await self.storage_service.get_object_meta(object_key)

        try:
            response = await self.pets_service.set_pet_photo_metadata(
                db,
                pet_id,
                user_id,
                object_key=object_key,
                content_type=metadata.content_type,
                size_bytes=metadata.size_bytes,
                etag=metadata.etag,
                uploaded_at=uploaded_at or self.storage_service.now_utc(),
            )
        except Exception as exc:
            try:
                cleaned_up = await self._cleanup_uploaded_object(object_key)
                if not cleaned_up:
                    raise RuntimeError("cleanup failed")
            except Exception as cleanup_exc:
                raise AppError(
                    "Failed to save pet photo metadata and clean up uploaded file",
                    status_code=500,
                    details={"cleanup_error": str(cleanup_exc)},
                ) from exc
            raise

        if previous_key and previous_key != object_key:
            try:
                await self.storage_service.delete_object(previous_key)
            except Exception as exc:
                try:
                    await self.pets_service.restore_pet_photo(db, pet_id, user_id, previous_snapshot)
                    await self.storage_service.delete_object(object_key)
                except Exception as rollback_exc:
                    raise AppError(
                        "Failed to delete previous pet photo and restore consistency",
                        status_code=500,
                        details={"rollback_error": str(rollback_exc)},
                    ) from exc
                raise AppError(
                    "Failed to delete previous pet photo from storage; changes were rolled back",
                    status_code=500,
                ) from exc

        return response

    async def replace_photo_with_bytes(
        self,
        db: AsyncSession,
        *,
        pet_id: int,
        user_id: int,
        payload: bytes,
        content_type: str,
    ) -> PetResponse:
        object_key = self.storage_service.build_pet_photo_object_key(
            user_id=user_id,
            pet_id=pet_id,
            content_type=content_type,
        )
        await self.storage_service.upload_bytes(
            object_key=object_key,
            payload=payload,
            content_type=content_type,
        )
        try:
            return await self.complete_upload(
                db,
                pet_id=pet_id,
                user_id=user_id,
                object_key=object_key,
                uploaded_at=self.storage_service.now_utc(),
                )
        except Exception:
            await self._cleanup_uploaded_object(object_key)
            raise

    async def delete_photo(self, db: AsyncSession, *, pet_id: int, user_id: int) -> bool:
        pet = await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        snapshot = self.pets_service.photo_snapshot(pet)
        if snapshot is None:
            return True

        await self.pets_service.clear_pet_photo(db, pet_id, user_id)
        try:
            await self.storage_service.delete_object(snapshot.object_key)
        except Exception as exc:
            try:
                await self.pets_service.restore_pet_photo(db, pet_id, user_id, snapshot)
            except Exception as rollback_exc:
                raise AppError(
                    "Failed to delete pet photo and restore database state",
                    status_code=500,
                    details={"rollback_error": str(rollback_exc)},
                ) from exc
            raise AppError(
                "Failed to delete pet photo from storage; changes were rolled back",
                status_code=500,
            ) from exc
        return True

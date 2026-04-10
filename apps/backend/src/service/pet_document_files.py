from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.exceptions import AppError
from src.schemas.documents import PetDocumentResponse, PetDocumentUploadUrlResponse
from src.service.pet_documents import PetDocumentsService
from src.service.storage import StorageService


class PetDocumentFilesService:
    def __init__(self) -> None:
        self.pet_documents_service = PetDocumentsService()
        self.storage_service = StorageService()

    async def _cleanup_uploaded_object(self, object_key: str | None) -> None:
        await self.storage_service.delete_object_quietly(object_key)

    async def create_upload_url(
        self,
        db: AsyncSession,
        *,
        pet_id: int,
        user_id: int,
        document_type_id: int,
        content_type: str,
        custom_name: str | None = None,
    ) -> PetDocumentUploadUrlResponse:
        object_key, custom_name = await self.pet_documents_service.build_object_key(
            db,
            pet_id=pet_id,
            user_id=user_id,
            document_type_id=document_type_id,
            content_type=content_type,
            custom_name=custom_name,
        )
        upload_url = await self.storage_service.create_upload_url(
            object_key=object_key,
            content_type=content_type,
        )
        return PetDocumentUploadUrlResponse(
            custom_name=custom_name,
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
        document_type_id: int,
        object_key: str,
        custom_name: str | None = None,
    ) -> PetDocumentResponse:
        if not self.storage_service.is_pet_document_key(
            object_key,
            user_id=user_id,
            pet_id=pet_id,
            document_type_id=document_type_id,
        ):
            raise AppError("Object key does not belong to this pet document", status_code=400)
        return await self.pet_documents_service.create_after_upload(
            db,
            pet_id,
            user_id,
            document_type_id=document_type_id,
            object_key=object_key,
            custom_name=custom_name,
        )

    async def create_from_bytes(
        self,
        db: AsyncSession,
        *,
        pet_id: int,
        user_id: int,
        document_type_id: int,
        payload: bytes,
        content_type: str,
        custom_name: str | None = None,
    ) -> PetDocumentResponse:
        object_key: str | None = None
        try:
            object_key, _custom_name = await self.pet_documents_service.build_object_key(
                db,
                pet_id=pet_id,
                user_id=user_id,
                document_type_id=document_type_id,
                content_type=content_type,
                custom_name=custom_name,
            )
            await self.storage_service.upload_bytes(
                object_key=object_key,
                payload=payload,
                content_type=content_type,
            )
            return await self.complete_upload(
                db,
                pet_id=pet_id,
                user_id=user_id,
                document_type_id=document_type_id,
                object_key=object_key,
                custom_name=custom_name,
            )
        except Exception:
            await self._cleanup_uploaded_object(object_key)
            raise

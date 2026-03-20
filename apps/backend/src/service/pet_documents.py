from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import AppError
from src.models import PetDocument
from src.schemas.documents import PetDocumentResponse, PetDocumentUpdateRequest
from src.service.pets import PetsService
from src.service.storage import StorageService


class PetDocumentsService:
    def __init__(self) -> None:
        self.pets_service = PetsService()
        self.storage_service = StorageService()

    def to_response(self, doc: PetDocument) -> PetDocumentResponse:
        return PetDocumentResponse(
            id=doc.id,
            pet_id=doc.pet_id,
            document_type_id=doc.document_id,
            custom_document_name_id=doc.custom_document_name_id,
            object_key=doc.object_key,
            original_filename=doc.original_filename,
            content_type=doc.content_type,
            size_bytes=doc.size_bytes,
            etag=doc.etag,
            uploaded_at=doc.uploaded_at,
        )

    async def list_for_pet(self, db: AsyncSession, pet_id: int, user_id: int) -> list[PetDocumentResponse]:
        await self.pets_service.get_pet_for_user(db, pet_id, user_id, allow_shared=True)
        result = await db.execute(select(PetDocument).where(PetDocument.pet_id == pet_id))
        return [self.to_response(doc) for doc in result.scalars().all()]

    async def get_one(self, db: AsyncSession, pet_id: int, document_row_id: int, user_id: int) -> PetDocument:
        await self.pets_service.get_pet_for_user(db, pet_id, user_id, allow_shared=True)
        result = await db.execute(
            select(PetDocument).where(
                PetDocument.id == document_row_id,
                PetDocument.pet_id == pet_id,
            )
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise AppError("Pet document not found", status_code=404)
        return doc

    async def create_after_upload(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
        *,
        document_type_id: int,
        custom_document_name_id: int | None,
        object_key: str,
        filename: str,
    ) -> PetDocumentResponse:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)

        allowed_prefix = f"users/{user_id}/pets/{pet_id}/documents/"
        if not object_key.startswith(allowed_prefix):
            raise AppError("Object key does not belong to this pet document", status_code=400)

        head = self.storage_service.head_object(object_key)
        content_type = head.get("ContentType")
        size_bytes_raw = head.get("ContentLength")
        etag_raw = head.get("ETag")

        doc = PetDocument(
            pet_id=pet_id,
            document_id=document_type_id,
            custom_document_name_id=custom_document_name_id,
            object_key=object_key,
            original_filename=filename,
            content_type=str(content_type) if content_type else None,
            size_bytes=int(size_bytes_raw) if isinstance(size_bytes_raw, int | float) else None,
            etag=str(etag_raw).strip('"') if etag_raw is not None else None,
            uploaded_at=datetime.now(datetime.UTC),
        )

        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return self.to_response(doc)

    async def update(
        self,
        db: AsyncSession,
        pet_id: int,
        document_row_id: int,
        payload: PetDocumentUpdateRequest,
        user_id: int,
    ) -> PetDocumentResponse:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        doc = await self.get_one(db, pet_id, document_row_id, user_id)

        data = payload.model_dump(exclude_unset=True)
        if "document_type_id" in data and data["document_type_id"] is not None:
            doc.document_id = data["document_type_id"]
        if "custom_document_name_id" in data:
            doc.custom_document_name_id = data["custom_document_name_id"]
        if "original_filename" in data:
            doc.original_filename = data["original_filename"]

        await db.commit()
        await db.refresh(doc)
        return self.to_response(doc)

    async def delete(self, db: AsyncSession, pet_id: int, document_row_id: int, user_id: int) -> None:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        doc = await self.get_one(db, pet_id, document_row_id, user_id)
        object_key = doc.object_key
        await db.delete(doc)
        await db.commit()
        self.storage_service.delete_object(object_key)
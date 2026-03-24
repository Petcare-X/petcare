from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import AppError
from src.models import DocumentType, PetDocument
from src.schemas.documents import (
    DocumentTypeResponse,
    PetDocumentResponse,
    PetDocumentUpdateRequest,
)
from src.service.pets import PetsService
from src.service.storage import StorageService


class PetDocumentsService:
    def __init__(self) -> None:
        self.pets_service = PetsService()
        self.storage_service = StorageService()

    def to_response(self, doc: PetDocument, *, document_type_name: str | None = None) -> PetDocumentResponse:
        return PetDocumentResponse(
            id=doc.id,
            pet_id=doc.pet_id,
            document_type_id=doc.document_id,
            document_type_name=document_type_name,
            custom_name=doc.custom_name,
            object_key=doc.object_key,
            content_type=doc.content_type,
            size_bytes=doc.size_bytes,
            etag=doc.etag,
            uploaded_at=doc.uploaded_at,
        )

    async def list_document_types(self, db: AsyncSession) -> list[DocumentTypeResponse]:
        result = await db.execute(select(DocumentType).order_by(DocumentType.id))
        return [
            DocumentTypeResponse(id=document_type.id, document_name=document_type.document_name)
            for document_type in result.scalars().all()
        ]

    async def get_document_type(self, db: AsyncSession, document_type_id: int) -> DocumentType:
        result = await db.execute(
            select(DocumentType).where(DocumentType.id == document_type_id)
        )
        document_type = result.scalar_one_or_none()
        if document_type is None:
            raise AppError("Document type not found", status_code=404)
        return document_type

    async def list_for_pet(self, db: AsyncSession, pet_id: int, user_id: int) -> list[PetDocumentResponse]:
        await self.pets_service.get_pet_for_user(db, pet_id, user_id, allow_shared=True)
        result = await db.execute(
            select(PetDocument, DocumentType.document_name)
            .join(DocumentType, DocumentType.id == PetDocument.document_id)
            .where(PetDocument.pet_id == pet_id)
            .order_by(PetDocument.id.desc())
        )
        return [
            self.to_response(doc, document_type_name=document_type_name)
            for doc, document_type_name in result.all()
        ]

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

    async def build_object_key(
        self,
        db: AsyncSession,
        *,
        pet_id: int,
        user_id: int,
        document_type_id: int,
        content_type: str,
    ) -> tuple[str, str]:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        document_type = await self.get_document_type(db, document_type_id)
        result = await db.execute(
            select(PetDocument.id)
            .where(
                PetDocument.pet_id == pet_id,
                PetDocument.document_id == document_type_id,
            )
            .order_by(PetDocument.id)
        )
        sequence_number = len(result.scalars().all())
        custom_name = self.storage_service.build_pet_document_custom_name(
            document_type.document_name,
            sequence_number=sequence_number,
        )
        object_key = self.storage_service.build_pet_document_object_key(
            user_id=user_id,
            pet_id=pet_id,
            document_type_id=document_type_id,
            custom_name=custom_name,
            content_type=content_type,
        )
        return object_key, custom_name

    async def create_after_upload(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
        *,
        document_type_id: int,
        object_key: str,
    ) -> PetDocumentResponse:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        document_type = await self.get_document_type(db, document_type_id)

        allowed_prefix = f"users/{user_id}/pets/{pet_id}/documents/{document_type_id}/"
        if not object_key.startswith(allowed_prefix):
            raise AppError("Object key does not belong to this pet document", status_code=400)

        head = await self.storage_service.head_object(object_key)
        content_type = head.get("ContentType")
        size_bytes_raw = head.get("ContentLength")
        etag_raw = head.get("ETag")

        doc = PetDocument(
            pet_id=pet_id,
            document_id=document_type_id,
            custom_name=Path(object_key).stem,
            object_key=object_key,
            content_type=str(content_type) if content_type else None,
            size_bytes=int(size_bytes_raw) if isinstance(size_bytes_raw, int | float) else None,
            etag=str(etag_raw).strip('"') if etag_raw is not None else None,
            uploaded_at=datetime.now(timezone.utc),
        )

        db.add(doc)
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            try:
                await self.storage_service.delete_object(object_key)
            except Exception as cleanup_exc:
                raise AppError(
                    "Failed to save document metadata and clean up uploaded file",
                    status_code=500,
                    details={"cleanup_error": str(cleanup_exc)},
                ) from exc
            raise
        await db.refresh(doc)
        return self.to_response(doc, document_type_name=document_type.document_name)

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
        document_type_name: str | None = None
        if "document_type_id" in data and data["document_type_id"] is not None:
            document_type = await self.get_document_type(db, data["document_type_id"])
            doc.document_id = data["document_type_id"]
            result = await db.execute(
                select(PetDocument.id)
                .where(
                    PetDocument.pet_id == pet_id,
                    PetDocument.document_id == data["document_type_id"],
                    PetDocument.id != doc.id,
                )
                .order_by(PetDocument.id)
            )
            doc.custom_name = self.storage_service.build_pet_document_custom_name(
                document_type.document_name,
                sequence_number=len(result.scalars().all()),
            )
            document_type_name = document_type.document_name
        else:
            document_type = await self.get_document_type(db, doc.document_id)
            document_type_name = document_type.document_name

        await db.commit()
        await db.refresh(doc)
        return self.to_response(doc, document_type_name=document_type_name)

    async def delete(self, db: AsyncSession, pet_id: int, document_row_id: int, user_id: int) -> None:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        doc = await self.get_one(db, pet_id, document_row_id, user_id)
        snapshot = {
            "id": doc.id,
            "pet_id": doc.pet_id,
            "document_id": doc.document_id,
            "custom_name": doc.custom_name,
            "object_key": doc.object_key,
            "content_type": doc.content_type,
            "size_bytes": doc.size_bytes,
            "etag": doc.etag,
            "uploaded_at": doc.uploaded_at,
        }
        object_key = doc.object_key
        await db.delete(doc)
        await db.commit()
        try:
            await self.storage_service.delete_object(object_key)
        except Exception as exc:
            db.add(PetDocument(**snapshot))
            try:
                await db.commit()
            except Exception as rollback_exc:
                await db.rollback()
                raise AppError(
                    "Failed to delete document file and restore database state",
                    status_code=500,
                    details={"rollback_error": str(rollback_exc)},
                ) from exc
            raise AppError(
                "Failed to delete document file from storage; changes were rolled back",
                status_code=500,
            ) from exc

from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import func, select
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
        custom_name: str | None = None,
    ) -> tuple[str, str]:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        document_type = await self.get_document_type(db, document_type_id)
        if custom_name is not None:
            base_name = self.storage_service.build_pet_document_custom_name(custom_name, sequence_number=0)
            duplicate_names_result = await db.execute(
                select(PetDocument.custom_name).where(
                    PetDocument.pet_id == pet_id,
                    PetDocument.document_id == document_type_id,
                )
            )
            existing_names = [
                name
                for name in duplicate_names_result.scalars().all()
                if isinstance(name, str) and (name == base_name or name.startswith(f"{base_name}_"))
            ]
            sequence_number = len(existing_names)
            object_key_name = self.storage_service.build_pet_document_custom_name(
                base_name,
                sequence_number=sequence_number,
            )
        else:
            total_count_result = await db.execute(
                select(func.count(PetDocument.id)).where(
                    PetDocument.pet_id == pet_id,
                    PetDocument.document_id == document_type_id,
                )
            )
            sequence_number = int(total_count_result.scalar_one())
            object_key_name = self.storage_service.build_pet_document_custom_name(
                document_type.document_name,
                sequence_number=sequence_number,
            )
        object_key = self.storage_service.build_pet_document_object_key(
            user_id=user_id,
            pet_id=pet_id,
            document_type_id=document_type_id,
            custom_name=object_key_name,
            content_type=content_type,
        )
        return object_key, object_key_name

    async def create_after_upload(
        self,
        db: AsyncSession,
        pet_id: int,
        user_id: int,
        *,
        document_type_id: int,
        object_key: str,
        custom_name: str | None = None,
    ) -> PetDocumentResponse:
        await self.pets_service.ensure_pet_owner(db, pet_id, user_id)
        document_type = await self.get_document_type(db, document_type_id)

        if not self.storage_service.is_pet_document_key(
            object_key,
            user_id=user_id,
            pet_id=pet_id,
            document_type_id=document_type_id,
        ):
            raise AppError("Object key does not belong to this pet document", status_code=400)

        metadata = await self.storage_service.get_object_meta(object_key)
        stored_custom_name = Path(object_key).stem
        if custom_name is not None:
            normalized = self.storage_service.build_pet_document_custom_name(custom_name, sequence_number=0)
            if not stored_custom_name.startswith(normalized):
                raise AppError("Custom name does not match uploaded object", status_code=400)

        doc = PetDocument(
            pet_id=pet_id,
            document_id=document_type_id,
            custom_name=stored_custom_name,
            object_key=object_key,
            content_type=metadata.content_type,
            size_bytes=metadata.size_bytes,
            etag=metadata.etag,
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
            doc.document_id = document_type.id
            document_type_name = document_type.document_name
        else:
            document_type = await self.get_document_type(db, doc.document_id)
            document_type_name = document_type.document_name

        if "custom_name" in data:
            resolved_name = (data["custom_name"] or "").strip()
            if not resolved_name:
                raise AppError("Custom name must not be empty", status_code=400)
            doc.custom_name = resolved_name

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

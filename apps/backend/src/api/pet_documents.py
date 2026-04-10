from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_db
from src.core.security import get_current_user_id
from src.schemas.documents import (
    DocumentTypeResponse,
    PetDocumentCompleteRequest,
    PetDocumentDownloadUrlResponse,
    PetDocumentResponse,
    PetDocumentUpdateRequest,
    PetDocumentUploadUrlRequest,
    PetDocumentUploadUrlResponse,
)
from src.service import PetDocumentFilesService, PetDocumentsService, StorageService

pet_documents_router = APIRouter(prefix="/documents", tags=["pet-documents"])
document_types_router = APIRouter(prefix="/document-types", tags=["document-types"])

pet_documents_service = PetDocumentsService()
pet_document_files_service = PetDocumentFilesService()
storage_service = StorageService()


@document_types_router.get("", response_model=list[DocumentTypeResponse])
async def list_document_types(
    db: AsyncSession = Depends(get_db),
):
    return await pet_documents_service.list_document_types(db)


@pet_documents_router.get("", response_model=list[PetDocumentResponse])
async def list_documents(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await pet_documents_service.list_for_pet(db, pet_id, current_user_id)


@pet_documents_router.post("/upload-url", response_model=PetDocumentUploadUrlResponse)
async def get_upload_url(
    pet_id: int,
    payload: PetDocumentUploadUrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await pet_document_files_service.create_upload_url(
        db,
        pet_id=pet_id,
        user_id=current_user_id,
        document_type_id=payload.document_type_id,
        content_type=payload.content_type,
        custom_name=payload.custom_name,
    )


@pet_documents_router.post("/complete", response_model=PetDocumentResponse)
async def complete_upload(
    pet_id: int,
    payload: PetDocumentCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await pet_document_files_service.complete_upload(
        db,
        pet_id=pet_id,
        user_id=current_user_id,
        document_type_id=payload.document_type_id,
        object_key=payload.object_key,
        custom_name=payload.custom_name,
    )

@pet_documents_router.patch("/{document_row_id}", response_model=PetDocumentResponse)
async def update_document(
    pet_id: int,
    document_row_id: int,
    payload: PetDocumentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    return await pet_documents_service.update(
        db,
        pet_id,
        document_row_id,
        payload,
        current_user_id,
    )


@pet_documents_router.get(
    "/{document_row_id}/download-url",
    response_model=PetDocumentDownloadUrlResponse,
)
async def get_download_url(
    pet_id: int,
    document_row_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    doc = await pet_documents_service.get_one(db, pet_id, document_row_id, current_user_id)
    document_type = await pet_documents_service.get_document_type(db, doc.document_id)
    download_url = await storage_service.create_download_url(doc.object_key)
    return PetDocumentDownloadUrlResponse(
        document_id=doc.id,
        document_type_name=document_type.document_name,
        custom_name=doc.custom_name,
        object_key=doc.object_key,
        download_url=download_url,
        expires_in=settings.MINIO_PRESIGNED_DOWNLOAD_TTL_SEC,
    )


@pet_documents_router.delete("/{document_row_id}")
async def delete_document(
    pet_id: int,
    document_row_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    await pet_documents_service.delete(db, pet_id, document_row_id, current_user_id)
    return {"deleted": True}

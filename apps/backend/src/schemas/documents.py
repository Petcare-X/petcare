from datetime import datetime

from pydantic import BaseModel, Field


class DocumentTypeResponse(BaseModel):
    id: int
    document_name: str


class PetDocumentUploadUrlRequest(BaseModel):
    document_type_id: int
    content_type: str = Field(min_length=1, max_length=100)
    custom_name: str | None = Field(default=None, min_length=1, max_length=255)

class PetDocumentUploadUrlResponse(BaseModel):
    custom_name: str
    object_key: str
    upload_url: str
    expires_in: int

class PetDocumentCompleteRequest(BaseModel):
    document_type_id: int
    object_key: str
    custom_name: str | None = Field(default=None, min_length=1, max_length=255)

class PetDocumentUpdateRequest(BaseModel):
    document_type_id: int | None = None
    custom_name: str | None = Field(default=None, min_length=1, max_length=255)

class PetDocumentResponse(BaseModel):
    id: int
    pet_id: int
    document_type_id: int
    document_type_name: str | None = None
    custom_name: str
    object_key: str
    content_type: str | None
    size_bytes: int | None
    etag: str | None
    uploaded_at: datetime | None

class PetDocumentDownloadUrlResponse(BaseModel):
    document_id: int
    document_type_name: str | None = None
    custom_name: str
    object_key: str
    download_url: str
    expires_in: int

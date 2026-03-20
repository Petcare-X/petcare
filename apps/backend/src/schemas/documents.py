from datetime import datetime

from pydantic import BaseModel, Field

class PetDocumentUploadUrlRequest(BaseModel):
    document_type_id: int
    custom_document_name_id: int | None = None
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)

class PetDocumentUploadUrlResponse(BaseModel):
    object_key: str
    upload_url: str
    expires_in: int

class PetDocumentCompleteRequest(BaseModel):
    document_type_id: int
    custom_document_name_id: int | None = None
    object_key: str
    filename: str = Field(min_length=1, max_length=255)

class PetDocumentUpdateRequest(BaseModel):
    document_type_id: int | None = None
    custom_document_name_id: int | None = None
    original_filename: str | None = Field(default=None, min_length=1, max_length=255)

class PetDocumentResponse(BaseModel):
    id: int
    pet_id: int
    document_type_id: int
    custom_document_name_id: int | None
    object_key: str
    original_filename: str | None
    content_type: str | None
    size_bytes: int | None
    etag: str | None
    uploaded_at: datetime | None

class PetDocumentDownloadUrlResponse(BaseModel):
    document_id: int
    object_key: str
    download_url: str
    expires_in: int
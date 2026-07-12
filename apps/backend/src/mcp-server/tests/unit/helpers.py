from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.infrastructure.storage.s3_client import S3Object


def make_pet_details_row(
    pet_name: str = "Barsik",
    animal_breed: str = "Maine Coon",
    birth_date: date | None = date(2020, 5, 15),
    weight: float = 4.5,
) -> dict:
    return {
        "pet_name": pet_name,
        "pet_sex": "male",
        "animal_breed": animal_breed,
        "pet_date_of_birth": birth_date,
        "pedigree": "RKF-123456",
        "pet_neck_girth": 20.0,
        "pet_breast_girth": 35.0,
        "pet_length": 45.0,
        "pet_is_sterylyzed": False,
        "pet_weight": weight,
        "pet_special_notes": "Loves treats",
    }


def make_pet_short_row(
    pet_name: str = "Barsik",
    animal_type: str = "Cat",
    animal_breed: str = "Maine Coon",
    birth_date: date | None = date(2020, 5, 15),
) -> dict:
    return {
        "pet_name": pet_name,
        "animal_type": animal_type,
        "animal_breed": animal_breed,
        "pet_date_of_birth": birth_date,
    }


def mock_pets_repo(
    *,
    details_row: dict | None = None,
    short_row: dict | None = None,
    pet_exists: bool = True,
    owner_id: str | None = "user-1",
) -> MagicMock:
    repo = MagicMock()
    repo.get_pet_details = AsyncMock(return_value=details_row)
    repo.get_pet_short_info = AsyncMock(return_value=short_row)
    repo.pet_exists_for_user = AsyncMock(return_value=pet_exists)
    repo.get_pet_owner_id = AsyncMock(
        return_value=None if owner_id is None else {"user_id": owner_id}
    )
    return repo


def make_document_row(
    document_id: int = 1,
    custom_name: str = "vaccine-cert",
    object_key: str = "pets/1/vaccine-cert.txt",
    document_type: str = "Vaccination",
    content_type: str = "text/plain",
    size_bytes: int = 128,
) -> dict:
    return {
        "document_id": document_id,
        "custom_name": custom_name,
        "object_key": object_key,
        "document_type": document_type,
        "content_type": content_type,
        "size_bytes": size_bytes,
    }


def mock_documents_repo(
    *,
    documents: list[dict] | None = None,
    document: dict | None = None,
) -> MagicMock:
    repo = MagicMock()
    repo.get_pet_documents = AsyncMock(return_value=documents or [])
    repo.get_pet_documents_by_upload_date = AsyncMock(return_value=documents or [])
    repo.get_document_for_pet_by_custom_name = AsyncMock(return_value=document)
    return repo


def make_s3_object(
    body: bytes = b"document content",
    content_type: str | None = "text/plain",
    etag: str | None = "mock-etag",
) -> S3Object:
    return S3Object(body=body, content_type=content_type, etag=etag)


def mock_s3_client(*, s3_obj: S3Object | None = None) -> MagicMock:
    client = MagicMock()
    client.download_object = AsyncMock(return_value=s3_obj or make_s3_object())
    return client


def make_clinic_row(
    vet_id: int = 1,
    vet_name: str = "City Vet",
    vet_city: str = "Moscow",
    vet_lat: float | None = 55.7558,
    vet_lon: float | None = 37.6176,
    working_hours: str | None = "09:00-18:00",
    is_24_7: bool = False,
    vet_phone: str = "+7-999-111-22-33",
    vet_website: str = "https://city-vet.example.com",
) -> dict:
    return {
        "vet_id": vet_id,
        "vet_name": vet_name,
        "vet_city": vet_city,
        "vet_streets": "Main street",
        "vet_building_number": "1",
        "vet_lat": vet_lat,
        "vet_lon": vet_lon,
        "vet_working_hours": working_hours,
        "vet_is_24_7": is_24_7,
        "vet_phone": vet_phone,
        "vet_website": vet_website,
        "vet_status": "active",
    }


def mock_clinics_repo(
    *,
    clinics: list[dict] | None = None,
    single_clinic: dict | None = None,
) -> MagicMock:
    repo = MagicMock()
    repo.search_by_city = AsyncMock(return_value=clinics or [])
    repo.list_active = AsyncMock(return_value=clinics or [])
    repo.get_active_by_id = AsyncMock(return_value=single_clinic)
    repo.get_active_location_by_name = AsyncMock(return_value=single_clinic)
    return repo

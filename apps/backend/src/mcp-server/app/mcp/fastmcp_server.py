from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import AsyncIterator

from fastmcp import FastMCP

from app.core.config import settings
from app.core.exceptions import ValidationAppError
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.storage.s3_client import S3StorageClient
from app.repository.clinics_repo import ClinicsRepository
from app.repository.documents_repo import DocumentsRepository
from app.repository.pets_repo import PetsRepository
from app.services.assistant_service import AssistantService
from app.services.clinics_service import ClinicsService
from app.services.documents_service import DocumentsService
from app.services.pets_service import PetsService


@asynccontextmanager
async def _service_scope() -> AsyncIterator[dict[str, object]]:
    async with AsyncSessionLocal() as db:
        storage_client = S3StorageClient()
        pets_repo = PetsRepository(db)
        documents_repo = DocumentsRepository(db)
        clinics_repo = ClinicsRepository(db)
        pets_service = PetsService(pets_repo)
        documents_service = DocumentsService(documents_repo, pets_repo, storage_client)
        clinics_service = ClinicsService(clinics_repo)
        assistant_service = AssistantService(pets_service, documents_service, clinics_service)
        yield {
            "pets": pets_service,
            "documents": documents_service,
            "clinics": clinics_service,
            "assistant": assistant_service,
        }


def _parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationAppError("uploaded_at must be an ISO date") from exc


def _parse_iso_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValidationAppError("current_datetime must be an ISO datetime") from exc


def create_fastmcp_server() -> FastMCP:
    mcp = FastMCP(
        name=f"{settings.APP_NAME} MCP",
        instructions=(
            "Use these tools only for pet-care workflows. "
            "Pets and documents are protected by user ownership. "
            "Clinics data includes only active veterinary clinics."
        ),
    )

    @mcp.tool(name="pets_get_pet_details")
    async def pets_get_pet_details(pet_id: int, user_id: str) -> dict:
        async with _service_scope() as services:
            return await services["pets"].get_pet_details(pet_id, user_id)  # type: ignore[union-attr]

    @mcp.tool(name="pets_get_pet_short_info")
    async def pets_get_pet_short_info(pet_id: int, user_id: str) -> dict:
        async with _service_scope() as services:
            return await services["pets"].get_pet_short_info(pet_id, user_id)  # type: ignore[union-attr]

    @mcp.tool(name="documents_get_pet_documents")
    async def documents_get_pet_documents(pet_id: int, user_id: str) -> list[dict]:
        async with _service_scope() as services:
            return await services["documents"].get_pet_documents(pet_id, user_id)  # type: ignore[union-attr]

    @mcp.tool(name="documents_get_pet_documents_by_upload_date")
    async def documents_get_pet_documents_by_upload_date(
        pet_id: int,
        user_id: str,
        uploaded_at: str,
    ) -> list[dict]:
        async with _service_scope() as services:
            return await services["documents"].get_pet_documents_by_upload_date(  # type: ignore[union-attr]
                pet_id,
                user_id,
                _parse_iso_date(uploaded_at),
            )

    @mcp.tool(name="documents_extract_pet_document_text_by_custom_name")
    async def documents_extract_pet_document_text_by_custom_name(
        pet_id: int,
        user_id: str,
        custom_name: str,
    ) -> dict:
        async with _service_scope() as services:
            return await services["documents"].extract_pet_document_text_by_custom_name(  # type: ignore[union-attr]
                pet_id,
                user_id,
                custom_name,
            )

    @mcp.tool(name="clinics_search_vet_clinics_by_city")
    async def clinics_search_vet_clinics_by_city(vet_city: str) -> list[dict]:
        async with _service_scope() as services:
            return await services["clinics"].search_vet_clinics_by_city(vet_city)  # type: ignore[union-attr]

    @mcp.tool(name="clinics_search_vet_clinics_by_location")
    async def clinics_search_vet_clinics_by_location(
        user_lat: float,
        user_lon: float,
        radius_km: float,
    ) -> list[dict]:
        async with _service_scope() as services:
            return await services["clinics"].search_vet_clinics_by_location(  # type: ignore[union-attr]
                user_lat,
                user_lon,
                radius_km,
            )

    @mcp.tool(name="clinics_filter_available_vet_clinics")
    async def clinics_filter_available_vet_clinics(
        current_datetime: str,
        vet_city: str | None = None,
        user_lat: float | None = None,
        user_lon: float | None = None,
        radius_km: float | None = None,
    ) -> list[dict]:
        async with _service_scope() as services:
            return await services["clinics"].filter_available_vet_clinics(  # type: ignore[union-attr]
                _parse_iso_datetime(current_datetime),
                vet_city=vet_city,
                user_lat=user_lat,
                user_lon=user_lon,
                radius_km=radius_km,
            )

    @mcp.tool(name="clinics_get_vet_contacts_by_address")
    async def clinics_get_vet_contacts_by_address(vet_id: int) -> dict:
        async with _service_scope() as services:
            return await services["clinics"].get_vet_contacts_by_address(vet_id)  # type: ignore[union-attr]

    @mcp.tool(name="clinics_get_vet_location_by_name")
    async def clinics_get_vet_location_by_name(vet_name: str, vet_city: str) -> dict:
        async with _service_scope() as services:
            return await services["clinics"].get_vet_location_by_name(vet_name, vet_city)  # type: ignore[union-attr]

    @mcp.tool(name="assistant_ask_petcare_assistant")
    async def assistant_ask_petcare_assistant(
        question: str,
        user_id: str | None = None,
        pet_id: int | None = None,
        vet_city: str | None = None,
        include_documents: bool = True,
        llm_name: str | None = None,
    ) -> dict:
        async with _service_scope() as services:
            return await services["assistant"].ask_petcare_assistant(  # type: ignore[union-attr]
                question=question,
                user_id=user_id,
                pet_id=pet_id,
                vet_city=vet_city,
                include_documents=include_documents,
                llm_name=llm_name,
            )

    return mcp

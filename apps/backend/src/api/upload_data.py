from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db

from src.service import ImportService
from src.schemas import ImportCsvResponse

upload_router = APIRouter(prefix="/upload-data", tags=["upload-data"])


@upload_router.post("/import-vet-csv", response_model=ImportCsvResponse)
async def import_vet_clinics_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    service = ImportService()
    return await service.import_vet_clinics(file=file, db=db)


@upload_router.post("/import-dogplace-csv", response_model=ImportCsvResponse)
async def import_dogplaces_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    service = ImportService()
    return await service.import_dogfriendly_places(file=file, db=db)

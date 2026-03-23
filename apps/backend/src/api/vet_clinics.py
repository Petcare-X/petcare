from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db

from src.service import VetImportService
from src.models import VetClinic
from src.schemas import GetVetClinic, ImportCsvResponse

vet_router = APIRouter(prefix="/vet-clinics", tags=["vet clinics"])

@vet_router.post("/import-csv", response_model=ImportCsvResponse)
async def import_vet_clinics_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    service = VetImportService()
    return await service.import_vet_clinics(file=file, db=db)


import os
import csv
from io import StringIO
from dotenv import load_dotenv
load_dotenv()

from fastapi import UploadFile, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.geocoder.geocoder import geocode_address

from src.models import VetClinic
from src.schemas import VetImportRow, ImportCsvResponse, ImportRowError, GetVetClinic, VetCreate

class VetImportService:
    async def import_vet_clinics(self, file: UploadFile, db: AsyncSession) -> ImportCsvResponse:
        content = await file.read()
        api_key = os.getenv("YANDEX_GEOCODER_API_KEY")

        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid file encoding")
        
        reader = csv.DictReader(StringIO(text))
        errors: list[ImportRowError] = []
        imported_count = 0
        total_rows = 0

        for row_number, row in enumerate(reader, start=2):
            total_rows += 1
        
            try:
                validated = VetImportRow.model_validate(row)

                try:
                    coordinates = await geocode_address(
                        api_key=api_key,
                        country="Россия",
                        city=validated.vet_city,
                        street=validated.vet_street,
                        house=validated.vet_building_number)
                    lat = coordinates["lat"]
                    lon = coordinates["lon"]
                    precision = coordinates["precision"]
                    
                except Exception as e:
                    lat = lon = None

                payload = VetCreate(
                    vet_name=validated.vet_name,
                    vet_city=validated.vet_city,
                    vet_street=validated.vet_street,
                    vet_building_number=validated.vet_building_number,
                    vet_phone=validated.vet_phone,
                    vet_website=str(validated.vet_website),
                    vet_working_hours=validated.vet_working_hours,
                    vet_is_24_7=validated.vet_is_24_7,
                    vet_status=validated.vet_status,
                    vet_lat=lat,
                    vet_lon=lon,
                    vet_geocoder_precision=precision
                )

                place = VetClinic(**payload.model_dump())
                db.add(place)
                imported_count += 1

            except Exception as e:
                errors.append(
                    ImportRowError(
                        row_number=row_number,
                        error=str(e),
                        raw_data=row,
                    )
                )

        await db.commit()

        return ImportCsvResponse(
            total_rows=total_rows,
            imported_rows=imported_count,
            skipped_rows=len(errors),
            errors=errors,
        )
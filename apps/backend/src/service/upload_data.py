import os
import csv
from io import StringIO
from dotenv import load_dotenv
load_dotenv()

from fastapi import UploadFile, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.geocoder.geocoder import geocode_address

from src.models import VetClinic, DogFriendlyPlace
from src.schemas import VetImportRow, VetCreate, DogPlaceCreate, DogPlaceImportRow
from src.schemas import ImportCsvResponse, ImportRowError

class ImportService:
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
                    vet_website=str(validated.vet_website) if validated.vet_website else None,
                    vet_working_hours=validated.vet_working_hours,
                    vet_is_24_7=validated.vet_is_24_7,
                    vet_status=validated.vet_status,
                    vet_lat=lat,
                    vet_lon=lon,
                    vet_geocoder_precision=precision
                )

                existing_result = await db.execute(
                    select(VetClinic).where(
                        VetClinic.vet_name == payload.vet_name,
                        VetClinic.vet_city == payload.vet_city,
                        VetClinic.vet_street == payload.vet_street,
                        VetClinic.vet_building_number == payload.vet_building_number,
                    )
                )
                existing_place = existing_result.scalar_one_or_none()
                if existing_place:
                    raise ValueError(
                        f"Vet clinic already exists: {existing_place.vet_name}"
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
    


    async def import_dogfriendly_places(self, file: UploadFile, db: AsyncSession) -> ImportCsvResponse:
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
                validated = DogPlaceImportRow.model_validate(row)

                try:
                    coordinates = await geocode_address(
                        api_key=api_key,
                        country="Россия",
                        city=validated.dogfriendly_place_city,
                        street=validated.dogfriendly_place_street,
                        house=validated.dogfriendly_place_building_number)
                    lat = coordinates["lat"]
                    lon = coordinates["lon"]
                    precision = coordinates["precision"]
                    
                except Exception as e:
                    lat = lon = None

                payload = DogPlaceCreate(
                    dogfriendly_place_name=validated.dogfriendly_place_name,
                    dogfriendly_place_city=validated.dogfriendly_place_city,
                    dogfriendly_place_street=validated.dogfriendly_place_street,
                    dogfriendly_place_building_number=validated.dogfriendly_place_building_number,
                    dogfriendly_place_working_hours=validated.dogfriendly_place_working_hours,
                    dogfriendly_place_is_24_7=validated.dogfriendly_place_is_24_7,
                    dogfriendly_place_status=validated.dogfriendly_place_status,
                    dogfriendly_place_lat=lat,
                    dogfriendly_place_lon=lon,
                    dogfriendly_place_geocoder_precision=precision
                )

                existing_result = await db.execute(
                    select(DogFriendlyPlace).where(
                        DogFriendlyPlace.dogfriendly_place_name == payload.dogfriendly_place_name,
                        DogFriendlyPlace.dogfriendly_place_city == payload.dogfriendly_place_city,
                        DogFriendlyPlace.dogfriendly_place_street == payload.dogfriendly_place_street,
                        DogFriendlyPlace.dogfriendly_place_building_number == payload.dogfriendly_place_building_number,
                    )
                )
                existing_place = existing_result.scalar_one_or_none()
                if existing_place:
                    raise ValueError(
                        f"Vet clinic already exists: {existing_place.dogfriendly_place_name}"
                    )

                place = DogFriendlyPlace(**payload.model_dump())
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
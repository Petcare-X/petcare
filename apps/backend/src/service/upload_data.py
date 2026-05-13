import csv
import os
from io import StringIO

from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import VetClinic, DogFriendlyPlace, GroomingSalon
from src.schemas import (
    DogPlaceCreate,
    DogPlaceImportRow,
    ImportCsvResponse,
    ImportRowError,
    VetCreate,
    VetImportRow,
    SalonCreate,
    SalonImportRow,
)
from src.third_party.geocoder.geocoder import geocode_address

load_dotenv()


class ImportService:
    async def _decode_csv_text(self, file: UploadFile) -> str:
        content = await file.read()
        try:
            return content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid file encoding") from exc

    async def _geocode(
        self,
        *,
        api_key: str | None,
        city: str,
        street: str,
        building_number: str,
    ) -> tuple[float | None, float | None, str | None]:
        try:
            coordinates = await geocode_address(
                api_key=api_key,
                country="Россия",
                city=city,
                street=street,
                house=building_number,
            )
        except Exception:
            return None, None, None

        return coordinates["lat"], coordinates["lon"], coordinates["precision"]

    @staticmethod
    async def _find_existing(
        db: AsyncSession,
        model,
        filters: dict[str, object],
    ):
        result = await db.execute(
            select(model).where(*(getattr(model, field_name) == value for field_name, value in filters.items()))
        )
        return result.scalar_one_or_none()

    async def _import_rows(
        self,
        *,
        file: UploadFile,
        db: AsyncSession,
        row_validator,
        payload_builder,
        model,
        duplicate_filters_builder,
        duplicate_error_builder,
        place_builder,
    ) -> ImportCsvResponse:
        text = await self._decode_csv_text(file)
        reader = csv.DictReader(StringIO(text))
        api_key = os.getenv("YANDEX_GEOCODER_API_KEY")

        errors: list[ImportRowError] = []
        imported_count = 0
        total_rows = 0

        for row_number, row in enumerate(reader, start=2):
            total_rows += 1

            try:
                validated = row_validator.model_validate(row)
                payload = await payload_builder(validated, api_key)

                existing_place = await self._find_existing(
                    db,
                    model,
                    duplicate_filters_builder(payload),
                )
                if existing_place:
                    raise ValueError(duplicate_error_builder(existing_place))

                db.add(place_builder(payload))
                imported_count += 1
            except Exception as exc:
                errors.append(
                    ImportRowError(
                        row_number=row_number,
                        error=str(exc),
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

    async def import_vet_clinics(self, file: UploadFile, db: AsyncSession) -> ImportCsvResponse:
        async def build_payload(validated: VetImportRow, api_key: str | None) -> VetCreate:
            lat, lon, precision = await self._geocode(
                api_key=api_key,
                city=validated.vet_city,
                street=validated.vet_street,
                building_number=validated.vet_building_number,
            )
            return VetCreate(
                vet_name=validated.vet_name,
                vet_city=validated.vet_city,
                vet_street=validated.vet_street,
                vet_building_number=validated.vet_building_number,
                vet_phone=validated.vet_phone,
                vet_working_hours=validated.vet_working_hours,
                vet_is_24_7=validated.vet_is_24_7,
                vet_status=validated.vet_status,
                vet_lat=lat,
                vet_lon=lon,
                vet_geocoder_precision=precision,
            )

        return await self._import_rows(
            file=file,
            db=db,
            row_validator=VetImportRow,
            payload_builder=build_payload,
            model=VetClinic,
            duplicate_filters_builder=lambda payload: {
                "vet_name": payload.vet_name,
                "vet_city": payload.vet_city,
                "vet_street": payload.vet_street,
                "vet_building_number": payload.vet_building_number,
            },
            duplicate_error_builder=lambda existing_place: (
                f"Vet clinic already exists: {existing_place.vet_name}"
            ),
            place_builder=lambda payload: VetClinic(**payload.model_dump()),
        )

    async def import_dogfriendly_places(self, file: UploadFile, db: AsyncSession) -> ImportCsvResponse:
        async def build_payload(
            validated: DogPlaceImportRow,
            api_key: str | None,
        ) -> DogPlaceCreate:
            lat, lon, precision = await self._geocode(
                api_key=api_key,
                city=validated.dogfriendly_place_city,
                street=validated.dogfriendly_place_street,
                building_number=validated.dogfriendly_place_building_number,
            )
            return DogPlaceCreate(
                dogfriendly_place_name=validated.dogfriendly_place_name,
                dogfriendly_place_city=validated.dogfriendly_place_city,
                dogfriendly_place_street=validated.dogfriendly_place_street,
                dogfriendly_place_building_number=validated.dogfriendly_place_building_number,
                dogfriendly_place_working_hours=validated.dogfriendly_place_working_hours,
                dogfriendly_place_status=validated.dogfriendly_place_status,
                dogfriendly_place_lat=lat,
                dogfriendly_place_lon=lon,
                dogfriendly_place_geocoder_precision=precision,
            )

        return await self._import_rows(
            file=file,
            db=db,
            row_validator=DogPlaceImportRow,
            payload_builder=build_payload,
            model=DogFriendlyPlace,
            duplicate_filters_builder=lambda payload: {
                "dogfriendly_place_name": payload.dogfriendly_place_name,
                "dogfriendly_place_city": payload.dogfriendly_place_city,
                "dogfriendly_place_street": payload.dogfriendly_place_street,
                "dogfriendly_place_building_number": payload.dogfriendly_place_building_number,
            },
            duplicate_error_builder=lambda existing_place: (
                f"Dog-friendly place already exists: {existing_place.dogfriendly_place_name}"
            ),
            place_builder=lambda payload: DogFriendlyPlace(**payload.model_dump()),
        )

    async def import_grooming_salons(self, file: UploadFile, db: AsyncSession) -> ImportCsvResponse:
        async def build_payload(
            validated: SalonImportRow,
            api_key: str | None,
        ) -> SalonCreate:
            lat, lon, precision = await self._geocode(
                api_key=api_key,
                city=validated.salon_city,
                street=validated.salon_street,
                building_number=validated.salon_building_number,
            )
            return SalonCreate(
                salon_name=validated.salon_name,
                salon_city=validated.salon_city,
                salon_street=validated.salon_street,
                salon_building_number=validated.salon_building_number,
                salon_working_hours=validated.salon_working_hours,
                salon_phone=validated.salon_phone,
                salon_website=str(validated.salon_website) if validated.salon_website else None,
                salon_status=validated.salon_status,
                salon_lat=lat,
                salon_lon=lon,
                salon_geocoder_precision=precision,
            )

        return await self._import_rows(
            file=file,
            db=db,
            row_validator=SalonImportRow,
            payload_builder=build_payload,
            model=GroomingSalon,
            duplicate_filters_builder=lambda payload: {
                "salon_name": payload.salon_name,
                "salon_city": payload.salon_city,
                "salon_street": payload.salon_street,
                "salon_building_number": payload.salon_building_number,
            },
            duplicate_error_builder=lambda existing_place: (
                f"Salon already exists: {existing_place.salon_name}"
            ),
            place_builder=lambda payload: GroomingSalon(**payload.model_dump(mode="json")),
        )
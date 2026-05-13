from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import DogFriendlyPlace, VetClinic, GroomingSalon
from src.schemas import DogPlaceMapPoint, VetMapPoint, SalonsMapPoint


class MapService:
    @staticmethod
    def _is_24_7_label(value: bool) -> str:
        return "да" if value else "нет"

    async def _get_active_entities(self, db: AsyncSession, model, status_field: str):
        result = await db.execute(
            select(model).where(getattr(model, status_field) == "active")
        )
        return list(result.scalars().all())

    async def get_vet_clinics_map_points(self, db: AsyncSession) -> list[VetMapPoint]:
        result = await self._get_active_entities(db, VetClinic, "vet_status")
        return [
            VetMapPoint(
                id=vet.id,
                vet_name=vet.vet_name,
                vet_lat=vet.vet_lat,
                vet_lon=vet.vet_lon,
                vet_working_hours=vet.vet_working_hours,
                vet_is_24_7=self._is_24_7_label(vet.vet_is_24_7),
                vet_street=vet.vet_street,
                vet_building_number=vet.vet_building_number,
                vet_phone="нет" if not vet.vet_phone else vet.vet_phone,
            )
            for vet in result
        ]

    async def get_dog_places_map_points(self, db: AsyncSession) -> list[DogPlaceMapPoint]:
        result = await self._get_active_entities(
            db,
            DogFriendlyPlace,
            "dogfriendly_place_status",
        )
        return [
            DogPlaceMapPoint(
                id=place.id,
                dogfriendly_place_name=place.dogfriendly_place_name,
                dogfriendly_place_lat=place.dogfriendly_place_lat,
                dogfriendly_place_lon=place.dogfriendly_place_lon,
                dogfriendly_place_street=place.dogfriendly_place_street,
                dogfriendly_place_building_number=place.dogfriendly_place_building_number,
                dogfriendly_place_working_hours=place.dogfriendly_place_working_hours,
            )
            for place in result
        ]

    async def get_salons_map_points(self, db: AsyncSession) -> list[SalonsMapPoint]:
        result = await self._get_active_entities(
            db,
            GroomingSalon,
            "salon_status",
        )
        return [
            SalonsMapPoint(
                id=salon.id,
                salon_name=salon.salon_name,
                salon_lat=salon.salon_lat,
                salon_lon=salon.salon_lon,
                salon_working_hours=salon.salon_working_hours,
                salon_street=salon.salon_street,
                salon_building_number=salon.salon_building_number,
                salon_phone=salon.salon_phone,
                salon_website=salon.salon_website,
            )
            for salon in result
        ]

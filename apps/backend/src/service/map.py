from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import VetMapPoint, DogPlaceMapPoint
from src.models import VetClinic, DogFriendlyPlace

class MapService:
    async def get_vet_clinics_map_points(self, db: AsyncSession) -> list[VetMapPoint]:
        vet_points = await db.execute(
            select(VetClinic).where(
                VetClinic.vet_status == "active"
            ))
        result = list(vet_points.scalars().all())
        return [
            VetMapPoint(
                id=vet.id,
                vet_name=vet.vet_name,
                vet_lat=vet.vet_lat,
                vet_lon=vet.vet_lon,
                vet_working_hours=vet.vet_working_hours,
                vet_is_24_7="да" if vet.vet_is_24_7 else "нет",
                vet_street=vet.vet_street,
                vet_building_number=vet.vet_building_number,
                vet_phone="нет" if not vet.vet_phone else vet.vet_phone
            )
            for vet in result
        ]
    
    async def get_dog_places_map_points(self, db: AsyncSession) -> list[DogPlaceMapPoint]:
        dog_places = await db.execute(
            select(DogFriendlyPlace).where(
                DogFriendlyPlace.dogfriendly_place_status == "active"
                ))
        result = list(dog_places.scalars().all())

        return [
            DogPlaceMapPoint(
                id=place.id,
                dogfriendly_place_name=place.dogfriendly_place_name,
                dogfriendly_place_lat=place.dogfriendly_place_lat,
                dogfriendly_place_lon=place.dogfriendly_place_lon,
                dogfriendly_place_street=place.dogfriendly_place_street,
                dogfriendly_place_building_number=place.dogfriendly_place_building_number,
                dogfriendly_place_working_hours=place.dogfriendly_place_working_hours,
                dogfriendly_place_is_24_7="да" if place.dogfriendly_place_is_24_7 else "нет"
            )
            for place in result
        ]
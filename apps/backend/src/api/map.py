from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.schemas import VetMapPoint, DogPlaceMapPoint
from src.service import MapService

map_router = APIRouter(prefix="/map-points", tags=["map-points"])


@map_router.get("/vet-clinics", status_code=200, response_model=list[VetMapPoint])
async def get_vet_clinics(
    db: AsyncSession = Depends(get_db),
    service: MapService = Depends(MapService),
):
    return await service.get_vet_clinics_map_points(db)


@map_router.get("/dogfriendly-places", status_code=200, response_model=list[DogPlaceMapPoint])
async def get_dogfriendly_places(
    db: AsyncSession = Depends(get_db),
    service: MapService = Depends(MapService),
):
    return await service.get_dog_places_map_points(db)

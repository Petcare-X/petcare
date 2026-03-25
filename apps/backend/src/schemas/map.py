from pydantic import BaseModel, ConfigDict

class VetMapPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vet_name: str
    vet_lat: float
    vet_lon: float
    vet_working_hours: str
    vet_is_24_7: str
    vet_street: str
    vet_building_number: str
    vet_phone: str | None

class DogPlaceMapPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dogfriendly_place_name: str
    dogfriendly_place_lat: float
    dogfriendly_place_lon: float
    dogfriendly_place_working_hours: str
    dogfriendly_place_is_24_7: str
    dogfriendly_place_street: str
    dogfriendly_place_building_number: str
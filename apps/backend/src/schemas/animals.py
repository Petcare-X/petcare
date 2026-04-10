from pydantic import BaseModel


class AnimalTypeResponse(BaseModel):
    id: int
    animal_name: str


class AnimalBreedResponse(BaseModel):
    id: int
    animal_breed: str
    animal_type_id: int

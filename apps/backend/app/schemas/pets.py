from pydantic import BaseModel, Field, field_validator
from pydantic.types import HttpUrl

from datetime import date
from typing import Optional, List

class BasePet(BaseModel):
    pet_name: str = Field(min_length=2, max_length=50)
    date_of_birth: Optional[date]
    type: str = Field(min_length=2, max_length=15)

    @field_validator("pet_name")
    def validate_name(cls, v):
        return v.strip()
    
class GetPet(BasePet):
    owner_name: int

class UpdatePet(BasePet):
    years_old: Optional[int] = None
    months_old: Optional[int] = None
    breed: Optional[str] = Field(default=None, min_length=2, max_length=50)  # 
    pedigree: Optional[str] = None
    length: Optional[float]
    neck_girth: Optional[float]
    breast_girth: Optional[float]
    is_sterylized: Optional[bool]

class PetDocument(BaseModel):
    document_name: str
    document_file: HttpUrl

class PetWithDocuments(BaseModel):
    documents: List[PetDocument]
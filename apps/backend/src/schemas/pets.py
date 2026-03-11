from pydantic import BaseModel, Field, field_validator, PastDate

from typing import Optional, List

from src.schemas.users import UserPublic

class BasePet(BaseModel):
    pet_name: str = Field(min_length=2, max_length=50)
    date_of_birth: Optional[PastDate]
    type: int
    breed: int 
    pedigree: Optional[bool] = True
    length: Optional[float]
    neck_girth: Optional[float]
    breast_girth: Optional[float]
    is_sterylized: Optional[bool] = False
    photo_url: str

    @field_validator("pet_name")
    def validate_name(cls, v):
        return v.strip()
    
class CreatePet(BasePet):
    user_id: int

class UpdatePet(BasePet):
    length: Optional[float]
    neck_girth: Optional[float]
    breast_girth: Optional[float]
    is_sterylized: Optional[bool]
    photo_url: Optional[str]

class PetDocument(BaseModel):
    document_name: str
    document_file: str

class PetWithDocuments(BaseModel):
    documents: List[PetDocument]

class PetSharing(BaseModel):
    other_user_id: UserPublic
    role: str
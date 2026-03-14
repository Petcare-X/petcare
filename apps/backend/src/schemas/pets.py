from pydantic import BaseModel, Field, field_validator, PastDate

from typing import Optional, List

from src.schemas.users import UserPublic

class PetCreate(BaseModel):
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


class PetResponse(BaseModel):
    id: int
    owner_user_id: int | None
    pet_name: str
    date_of_birth: Optional[PastDate]
    type: int
    breed: int
    pedigree: Optional[bool]
    length: Optional[float]
    neck_girth: Optional[float]
    breast_girth: Optional[float]
    is_sterylized: Optional[bool]
    photo_url: str
    is_shared: bool = False


class UpdatePet(BaseModel):
    pet_name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    date_of_birth: Optional[PastDate] = None
    type: Optional[int] = None
    breed: Optional[int] = None
    pedigree: Optional[bool] = None
    length: Optional[float] = None
    neck_girth: Optional[float] = None
    breast_girth: Optional[float] = None
    is_sterylized: Optional[bool] = None
    photo_url: Optional[str] = None

    @field_validator("pet_name")
    def validate_name(cls, v):
        if v is None:
            return v
        return v.strip()


CreatePet = PetCreate
BasePet = PetCreate

class PetDocument(BaseModel):
    document_name: str
    document_file: str

class PetWithDocuments(BaseModel):
    documents: List[PetDocument]

class PetSharing(BaseModel):
    other_user_id: UserPublic
    role: str

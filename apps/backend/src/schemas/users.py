from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from datetime import date
from typing import Optional

# базовый юзер-класс
class BaseUser(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    role: str # owner, co-owner, helper, doctor?

class CreateUser(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone_number: PhoneNumber
    password: str
    birth_date: date
    photo_url: str 

    @field_validator("name")
    def validate_name(cls, v):
        return v.strip()

class UpdateUser(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    photo_url: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None
    password: Optional[str] = None

class UserPrivate(BaseUser):
    email: EmailStr
    phone_number: PhoneNumber
    password: str
    birth_date: date
    photo_url: str

class UserPublic(BaseUser):
    photo_path: str

class UserSettings(BaseModel):
    notify_push: bool = Field(default=False)
    notify_email: bool = Field(default=False)

class PictureUpload(BaseModel):
    photo_url: str
    
class UpdateUserContacts(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None
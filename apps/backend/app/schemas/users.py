from pydantic import BaseModel, Field, field_validator
from pydantic.types import EmailStr, HttpUrl
from pydantic_extra_types.phone_numbers import PhoneNumber

from datetime import date
from typing import Optional

# базовый юзер-класс
class BaseUser(BaseModel):
    id: int
    name: int = Field(min_length=2, max_length=50)

class CreateUser(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone_number: PhoneNumber
    password: str
    birth_date: date
    photo_url: HttpUrl # как хранятся ссылки на фото? 

    @field_validator("name")
    def validate_name(cls, v):
        return v.strip()

class UpdateDataUser(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    photo_url: Optional[HttpUrl] = None

class UpdateContactsUser(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None
    password: Optional[str] = None

class UserPrivate(BaseUser):
    email: EmailStr
    phone_number: PhoneNumber
    password: str
    birth_date: date
    photo_url: HttpUrl

class UserPublic(BaseUser):
    photo_path: str

class UserSettings(BaseModel):
    notify_push: bool = Field(default=False)
    notify_email: bool = Field(default=False)

class PictureUpload(BaseModel):
    photo_path: str
<<<<<<< HEAD
from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator
=======
from pydantic import BaseModel, EmailStr, Field, field_validator
>>>>>>> KAN-25-Профиль-питомца
from pydantic_extra_types.phone_numbers import PhoneNumber

from datetime import date
from typing import Optional

<<<<<<< HEAD

class BaseUser(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=50)

=======
# базовый юзер-класс
class BaseUser(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    role: str # owner, co-owner, helper, doctor?
>>>>>>> KAN-25-Профиль-питомца

class CreateUser(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone_number: PhoneNumber
    password: str
    birth_date: date
<<<<<<< HEAD
    photo_url: HttpUrl

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return v.strip()


class UpdateDataUser(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    photo_url: Optional[HttpUrl] = None


class UpdateContactsUser(BaseModel):
=======
    photo_url: str 

    @field_validator("name")
    def validate_name(cls, v):
        return v.strip()

class UpdateUser(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    photo_url: Optional[str] = None
>>>>>>> KAN-25-Профиль-питомца
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None
    password: Optional[str] = None

<<<<<<< HEAD

=======
>>>>>>> KAN-25-Профиль-питомца
class UserPrivate(BaseUser):
    email: EmailStr
    phone_number: PhoneNumber
    password: str
    birth_date: date
<<<<<<< HEAD
    photo_url: HttpUrl

=======
    photo_url: str
>>>>>>> KAN-25-Профиль-питомца

class UserPublic(BaseUser):
    photo_path: str

<<<<<<< HEAD

=======
>>>>>>> KAN-25-Профиль-питомца
class UserSettings(BaseModel):
    notify_push: bool = Field(default=False)
    notify_email: bool = Field(default=False)

<<<<<<< HEAD

class PictureUpload(BaseModel):
    photo_path: str
=======
class PictureUpload(BaseModel):
    photo_url: str
>>>>>>> KAN-25-Профиль-питомца

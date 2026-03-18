from datetime import date

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber


class CreateUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_name: str = Field(
        min_length=2,
        max_length=50,
        validation_alias=AliasChoices("user_name", "name"),
    )
    user_email: EmailStr = Field(
        validation_alias=AliasChoices("user_email", "email"),
    )
    user_phone_number: PhoneNumber = Field(
        validation_alias=AliasChoices("user_phone_number", "phone_number"),
    )
    password: str
    user_date_of_birth: date = Field(
        validation_alias=AliasChoices("user_date_of_birth", "birth_date"),
    )
    user_photo: str = Field(
        validation_alias=AliasChoices("user_photo", "photo_url"),
    )

    @field_validator("user_name")
    def validate_name(cls, value: str) -> str:
        return value.strip()


class UpdateUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        validation_alias=AliasChoices("user_name", "name"),
    )
    user_photo: str | None = Field(
        default=None,
        validation_alias=AliasChoices("user_photo", "photo_url"),
    )
    user_email: EmailStr | None = Field(
        default=None,
        validation_alias=AliasChoices("user_email", "email"),
    )
    user_phone_number: PhoneNumber | None = Field(
        default=None,
        validation_alias=AliasChoices("user_phone_number", "phone_number"),
    )
    password: str | None = None

    @field_validator("user_name")
    def validate_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_name: str
    user_photo: str


class UserPrivate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_name: str
    user_email: EmailStr
    user_phone_number: str
    user_date_of_birth: date
    user_photo: str
    telegram_id: int | None
    auth_provider: str


class UserSettings(BaseModel):
    notify_push: bool = Field(default=False)
    notify_email: bool = Field(default=False)


class PictureUpload(BaseModel):
    user_photo: str = Field(
        validation_alias=AliasChoices("user_photo", "photo_url"),
    )

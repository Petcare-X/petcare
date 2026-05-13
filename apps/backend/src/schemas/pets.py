from datetime import date, datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

from src.pet_measurements import PET_MEASUREMENT_RULES, validate_pet_measurements_consistency, validate_pet_measurement_value
from src.schemas.users import UserPublic


class PetCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pet_name: str = Field(min_length=2, max_length=50)
    pet_date_of_birth: date = Field(
        validation_alias=AliasChoices("pet_date_of_birth", "date_of_birth"),
    )
    pet_sex: str = Field(
        validation_alias=AliasChoices("pet_sex", "sex"))
    animal_type_id: int = Field(
        validation_alias=AliasChoices("animal_type_id", "type"),
    )
    animal_breed_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("animal_breed_id", "breed"),
    )
    animal_breed_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("animal_breed_name", "breed_name"),
    )
    pedigree: bool = Field(
        validation_alias=AliasChoices("pedigree", "pet_pedigree"),
    )
    pet_neck_girth: float = Field(
        validation_alias=AliasChoices("pet_neck_girth", "neck_girth"),
    )
    pet_breast_girth: float = Field(
        validation_alias=AliasChoices("pet_breast_girth", "breast_girth"),
    )
    pet_length: float = Field(
        validation_alias=AliasChoices("pet_length", "length"),
    )
    pet_weight: float
    pet_is_sterylyzed: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_is_sterylyzed", "is_sterylized"),
    )
    pet_special_notes: str | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_special_notes", "special_notes"))
    pet_photo_object_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "pet_photo_object_key",
            "pet_photo",
            "photo_url",
        ),
    )
    pet_photo_content_type: str | None = None
    pet_photo_size_bytes: int | None = Field(default=None, ge=0)
    pet_photo_etag: str | None = None
    pet_photo_uploaded_at: datetime | None = None

    @field_validator("pet_name")
    def validate_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("animal_breed_name")
    def validate_breed_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()

    @field_validator(*PET_MEASUREMENT_RULES.keys())
    def validate_measurements(cls, value: float, info) -> float:
        validate_pet_measurement_value(info.field_name, value)
        return value

    @model_validator(mode="after")
    def validate_measurements_consistency(self):
        if self.animal_breed_id is None and not self.animal_breed_name:
            raise ValueError("Animal breed id or breed name is required.")

        validate_pet_measurements_consistency(
            {
                "pet_neck_girth": self.pet_neck_girth,
                "pet_breast_girth": self.pet_breast_girth,
            }
        )
        return self


class PetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    pet_name: str
    pet_date_of_birth: date
    pet_sex: str
    animal_type_id: int
    animal_breed_id: int
    pedigree: bool
    pet_neck_girth: float
    pet_breast_girth: float
    pet_length: float
    pet_weight: float
    pet_special_notes: str | None
    pet_is_sterylyzed: bool | None
    pet_photo_object_key: str | None
    pet_photo_content_type: str | None
    pet_photo_size_bytes: int | None
    pet_photo_etag: str | None
    pet_photo_uploaded_at: datetime | None
    is_shared: bool = False


class UpdatePet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pet_name: str | None = Field(default=None, min_length=2, max_length=50)
    pet_date_of_birth: date | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_date_of_birth", "date_of_birth"),
    )
    pet_sex: str | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_sex", "sex"))
    animal_type_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("animal_type_id", "type"),
    )
    animal_breed_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("animal_breed_id", "breed"),
    )
    pedigree: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("pedigree", "pet_pedigree"),
    )
    pet_neck_girth: float | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_neck_girth", "neck_girth"),
    )
    pet_breast_girth: float | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_breast_girth", "breast_girth"),
    )
    pet_length: float | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_length", "length"),
    )
    pet_weight: float | None = None
    pet_is_sterylyzed: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_is_sterylyzed", "is_sterylized"),
    )
    pet_special_notes: str | None = Field(
        default=None,
        validation_alias=AliasChoices("pet_special_notes", "special_notes"))
    pet_photo_object_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "pet_photo_object_key",
            "pet_photo",
            "photo_url",
        ),
    )
    pet_photo_content_type: str | None = None
    pet_photo_size_bytes: int | None = Field(default=None, ge=0)
    pet_photo_etag: str | None = None
    pet_photo_uploaded_at: datetime | None = None

    @field_validator("pet_name")
    def validate_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()

    @field_validator(*PET_MEASUREMENT_RULES.keys())
    def validate_optional_measurements(cls, value: float | None, info) -> float | None:
        if value is None:
            return value
        validate_pet_measurement_value(info.field_name, value)
        return value

    @model_validator(mode="after")
    def validate_optional_measurements_consistency(self):
        validate_pet_measurements_consistency(
            {
                "pet_neck_girth": self.pet_neck_girth,
                "pet_breast_girth": self.pet_breast_girth,
            }
        )
        return self


CreatePet = PetCreate
BasePet = PetCreate

class PetSharing(BaseModel):
    other_user: UserPublic


class PetPhotoUploadUrlRequest(BaseModel):
    content_type: str


class PetPhotoUploadUrlResponse(BaseModel):
    object_key: str
    upload_url: str
    expires_in: int


class PetPhotoCompleteRequest(BaseModel):
    object_key: str


class PetPhotoDownloadUrlResponse(BaseModel):
    object_key: str
    download_url: str
    expires_in: int

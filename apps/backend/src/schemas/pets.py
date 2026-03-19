from datetime import date, datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from src.schemas.users import UserPublic


class PetCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pet_name: str = Field(min_length=2, max_length=50)
    pet_date_of_birth: date = Field(
        validation_alias=AliasChoices("pet_date_of_birth", "date_of_birth"),
    )
    animal_type_id: int = Field(
        validation_alias=AliasChoices("animal_type_id", "type"),
    )
    animal_breed_id: int = Field(
        validation_alias=AliasChoices("animal_breed_id", "breed"),
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
    pet_photo_object_key: str = Field(
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


class PetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    pet_name: str
    pet_date_of_birth: date
    animal_type_id: int
    animal_breed_id: int
    pedigree: bool
    pet_neck_girth: float
    pet_breast_girth: float
    pet_length: float
    pet_weight: float
    pet_is_sterylyzed: bool | None
    pet_photo_object_key: str
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


CreatePet = PetCreate
BasePet = PetCreate


class PetDocument(BaseModel):
    document_name: str
    document_file: str


class PetWithDocuments(BaseModel):
    documents: list[PetDocument]


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

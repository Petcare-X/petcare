from pydantic import BaseModel, AnyUrl, field_validator
import re
from typing import List


class VetImportRow(BaseModel):
    vet_name: str
    vet_city: str
    vet_street: str
    vet_building_number: str
    vet_working_hours: str
    vet_is_24_7: bool
    vet_status: str
    vet_phone: str

    @field_validator("vet_name", "vet_city", "vet_street", "vet_phone", mode="before")
    @classmethod
    def strip_string(cls, value):
        if value:
            return value.strip()
        return value
    
    @field_validator("vet_is_24_7", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, bool):
            return value
        else:
            norm_value = value.lower().strip()
            if norm_value in {"true", "1", "yes", "y", "да"}:
                return True
            if norm_value in {"false", "0", "no", "n", "нет"}:
                return False
            
    @field_validator("vet_phone")
    def validate_phone(cls, value):
        if value is None:
            return None
        pattern = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
        if re.match(pattern, value):
            return value
        return None
    
    @field_validator("vet_street", "vet_building_number", mode="before")
    @classmethod
    def clean_invisible_chars(cls, value):
        if isinstance(value, str):
            value = value.replace("\u200b", "").strip()
        return value

class VetCreate(BaseModel):
    vet_lat: float | None = None
    vet_lon: float | None = None
    vet_geocoder_precision: str | None = None
    vet_name: str
    vet_city: str
    vet_street: str
    vet_building_number: str
    vet_working_hours: str
    vet_is_24_7: bool
    vet_status: str
    vet_phone: str

    @field_validator("vet_name", "vet_city", "vet_street", "vet_phone", mode="before")
    @classmethod
    def strip_string(cls, value):
        if value:
            return value.strip()
        return value
    
    @field_validator("vet_is_24_7", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, bool):
            return value
        else:
            norm_value = value.lower().strip()
            if norm_value in {"true", "1", "yes", "y", "да"}:
                return True
            if norm_value in {"false", "0", "no", "n", "нет"}:
                return False
            
    @field_validator("vet_phone")
    def validate_phone(cls, value):
        if value is None:
            return None
        pattern = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
        if re.match(pattern, value):
            return value
        return None

    @field_validator("vet_lat", "vet_lon", mode="before")
    @classmethod
    def parse_float(cls, value):
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if value == "":
                return None
        return float(value)
    

class DogPlaceCreate(BaseModel):
    dogfriendly_place_lat: float | None = None
    dogfriendly_place_lon: float | None = None
    dogfriendly_place_geocoder_precision: str | None = None
    dogfriendly_place_name: str
    dogfriendly_place_city: str
    dogfriendly_place_street: str
    dogfriendly_place_building_number: str
    dogfriendly_place_working_hours: str
    dogfriendly_place_status: str

    @field_validator("dogfriendly_place_name", 
                     "dogfriendly_place_city", 
                     "dogfriendly_place_street", 
                     mode="before")
    @classmethod
    def strip_string(cls, value):
        if value:
            return value.strip()
        return value

    @field_validator("dogfriendly_place_lat", 
                     "dogfriendly_place_lon", 
                     mode="before")
    @classmethod
    def parse_float(cls, value):
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if value == "":
                return None
        return float(value)

class DogPlaceImportRow(BaseModel):
    dogfriendly_place_name: str
    dogfriendly_place_city: str
    dogfriendly_place_street: str
    dogfriendly_place_building_number: str
    dogfriendly_place_working_hours: str
    dogfriendly_place_status: str

    @field_validator("dogfriendly_place_name", 
                     "dogfriendly_place_city", 
                     "dogfriendly_place_street", 
                     mode="before")
    @classmethod
    def strip_string(cls, value):
        if value:
            return value.strip()
        return value
    
    @field_validator("dogfriendly_place_street", 
                     "dogfriendly_place_building_number", mode="before")
    @classmethod
    def clean_invisible_chars(cls, value):
        if isinstance(value, str):
            value = value.replace("\u200b", "").strip()
        return value
    
class SalonCreate(BaseModel):
    salon_lat: float | None = None
    salon_lon: float | None = None
    salon_geocoder_precision: str | None = None
    salon_name: str
    salon_city: str
    salon_street: str
    salon_building_number: str
    salon_working_hours: str
    salon_phone: str
    salon_website: AnyUrl | None
    salon_status: str

    @field_validator("salon_name", 
                     "salon_city", 
                     "salon_street", 
                     mode="before")
    @classmethod
    def strip_string(cls, value):
        if value:
            return value.strip()
        return value

    @field_validator("salon_lat", 
                     "salon_lon", 
                     mode="before")
    @classmethod
    def parse_float(cls, value):
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if value == "":
                return None
        return float(value)
    
    @field_validator("salon_website", mode="before")
    @classmethod
    def normalize_salon_website(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if value == "":
                return None

            if not value.startswith(("http://", "https://")):
                value = f"https://{value}"

        return value

class SalonImportRow(BaseModel):
    salon_name: str
    salon_city: str
    salon_street: str
    salon_building_number: str
    salon_phone: str
    salon_website: AnyUrl | None
    salon_working_hours: str

    salon_status: str

    @field_validator("salon_name", 
                     "salon_city", 
                     "salon_street", 
                     mode="before")
    @classmethod
    def strip_string(cls, value):
        if value:
            return value.strip()
        return value
    
    @field_validator("salon_street", 
                     "salon_building_number", mode="before")
    @classmethod
    def clean_invisible_chars(cls, value):
        if isinstance(value, str):
            value = value.replace("\u200b", "").strip()
        return value
    
    @field_validator("salon_website", mode="before")
    @classmethod
    def normalize_salon_website(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if value == "":
                return None

            if not value.startswith(("http://", "https://")):
                value = f"https://{value}"

        return value

class ImportRowError(BaseModel):
    row_number: int
    error: str
    raw_data: dict


class ImportCsvResponse(BaseModel):
    total_rows: int
    imported_rows: int
    skipped_rows: int
    errors: List[ImportRowError]
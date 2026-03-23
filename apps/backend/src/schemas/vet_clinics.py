from pydantic import BaseModel, EmailStr, Field, AnyUrl, field_validator
import re
from typing import Optional, List

class GetVetClinic(BaseModel):
    vet_name: str
    vet_city: str
    vet_street: str
    vet_building_number: str
    vet_working_hours: str 
    vet_is_24_7: bool
    vet_status: str
    vet_phone: str 
    vet_website: str


class VetImportRow(BaseModel):
    vet_name: str
    vet_city: str
    vet_street: str
    vet_building_number: str
    vet_working_hours: str
    vet_is_24_7: bool = False
    vet_status: str
    vet_phone: str | None = None
    vet_website: AnyUrl

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
    vet_is_24_7: bool = False
    vet_status: str
    vet_phone: str | None = None
    vet_website: str

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

class ImportRowError(BaseModel):
    row_number: int
    error: str
    raw_data: dict


class ImportCsvResponse(BaseModel):
    total_rows: int
    imported_rows: int
    skipped_rows: int
    errors: List[ImportRowError]
from sqlalchemy import String, Text, Numeric, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated
from datetime import datetime

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class VetClinic(Base):
    __tablename__ = "vet_clinics"
    
    id: Mapped[int_primary_key]
    vet_name: Mapped[str] = mapped_column(String(50))
    vet_city: Mapped[str] = mapped_column(String(50))
    vet_street: Mapped[str] = mapped_column(String(127))
    vet_building_number: Mapped[str] = mapped_column(String(20))
    vet_lat: Mapped[int] = mapped_column(Numeric)
    vet_lon: Mapped[int] = mapped_column(Numeric)
    vet_geocoder_precision: Mapped[str] = mapped_column(String(50))
    vet_working_hours: Mapped[str] = mapped_column(String(255))
    vet_is_24_7: Mapped[bool] = mapped_column(Boolean)
    vet_status: Mapped[str] = mapped_column(String(20))
    vet_phone: Mapped[str] = mapped_column(String(16), nullable=True)
    vet_website: Mapped[str | None] = mapped_column(Text)
    vet_last_verified: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
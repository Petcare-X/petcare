from sqlalchemy import String, Numeric, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated
from datetime import datetime

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class DogFriendlyPlace(Base):
    __tablename__ = "dog_friendly_places"

    __table_args__ = (
        UniqueConstraint(
            "dogfriendly_place_name",
            "dogfriendly_place_city",
            "dogfriendly_place_street",
            "dogfriendly_place_building_number",
            name="unique_dog_friendly_place"
        ),
    )
    
    id: Mapped[int_primary_key]
    dogfriendly_place_name: Mapped[str] = mapped_column(String(50))
    dogfriendly_place_city: Mapped[str] = mapped_column(String(50))
    dogfriendly_place_street: Mapped[str] = mapped_column(String(127))
    dogfriendly_place_building_number: Mapped[str] = mapped_column(String(20))
    dogfriendly_place_lat: Mapped[int] = mapped_column(Numeric)
    dogfriendly_place_lon: Mapped[int] = mapped_column(Numeric)
    dogfriendly_place_geocoder_precision: Mapped[str] = mapped_column(String(50))
    dogfriendly_place_working_hours: Mapped[str] = mapped_column(String(255))
    dogfriendly_place_status: Mapped[str] = mapped_column(String(20))
    dogfriendly_place_last_verified: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
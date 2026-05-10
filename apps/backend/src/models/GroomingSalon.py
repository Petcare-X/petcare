from sqlalchemy import String, Numeric, DateTime, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated
from datetime import datetime

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class GroomingSalon(Base):
    __tablename__ = "grooming_salons"

    __table_args__ = (
        UniqueConstraint(
            "salon_name",
            "salon_city",
            "salon_street",
            "salon_building_number",
            name="unique_grooming_salon"
        ),
    )
    
    id: Mapped[int_primary_key]
    salon_name: Mapped[str] = mapped_column(String(50))
    salon_city: Mapped[str] = mapped_column(String(50))
    salon_street: Mapped[str] = mapped_column(String(127))
    salon_building_number: Mapped[str] = mapped_column(String(20))
    salon_lat: Mapped[int] = mapped_column(Numeric)
    salon_lon: Mapped[int] = mapped_column(Numeric)
    salon_geocoder_precision: Mapped[str] = mapped_column(String(50))
    salon_working_hours: Mapped[str] = mapped_column(String(255))
    salon_phone: Mapped[str] = mapped_column(String(16))
    salon_website: Mapped[str | None] = mapped_column(String, nullable=True)
    salon_status: Mapped[str] = mapped_column(String(20))
    salon_last_verified: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
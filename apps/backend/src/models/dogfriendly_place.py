from sqlalchemy import String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated
from decimal import Decimal

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class DogFriendlyPlace(Base):
    __tablename__ = "dog_friendly_places"

    id: Mapped[int_primary_key]
    dogfriendly_place_name: Mapped[str] = mapped_column(String(100))
    dogfriendly_place_address: Mapped[str] = mapped_column(String(200))
    dogfriendly_place_rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    dogfriendly_place_work_hours: Mapped[str] = mapped_column(String(100))
    dogfriendly_place_contacts: Mapped[str] = mapped_column(String(100))
    dogfriendly_place_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dogfriendly_place_photo: Mapped[str | None] = mapped_column(Text, nullable=True)
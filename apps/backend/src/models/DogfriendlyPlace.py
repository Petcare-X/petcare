from sqlalchemy import String, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class DogFriendlyPlace(Base):
    __tablename__ = "dog_friendly_places"
    
    id: Mapped[int_primary_key]
    dogfriendly_place_name: Mapped[str] = mapped_column(String(50))
    dogfriendly_place_address: Mapped[str] = mapped_column(String(50))
    dogfriendly_place_rating: Mapped[int] = mapped_column(Numeric)
    dogfriendly_place_work_hours: Mapped[str] = mapped_column(String(50))
    dogfriendly_place_contacts: Mapped[str] = mapped_column(String(50))
    dogfriendly_place_description: Mapped[str] = mapped_column(Text)
    dogfriendly_place_photo: Mapped[str] = mapped_column(Text)
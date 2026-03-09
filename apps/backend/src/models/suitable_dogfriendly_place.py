from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class SuitableDogFriendlyPlace(Base):
    __tablename__ = "suitable_dogfriendly_places"

    id: Mapped[int_primary_key]
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets_info.id", ondelete="CASCADE"))
    place_id: Mapped[int] = mapped_column(Integer, ForeignKey("dog_friendly_places.id", ondelete="CASCADE"))

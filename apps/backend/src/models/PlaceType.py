from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated
from datetime import datetime

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class DogFriendlyPlaceType(Base):
    __tablename__ = "dog_friendly_place_types"
    
    id: Mapped[int_primary_key]
    place_name: Mapped[str] = mapped_column(String(50), unique=True)
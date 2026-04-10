from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class AnimalType(Base):
    __tablename__ = "animals_types"
    
    id: Mapped[int_primary_key]
    animal_name: Mapped[str] = mapped_column(String(50), unique=True)
    breeds = relationship("AnimalBreed", back_populates="animal_type")

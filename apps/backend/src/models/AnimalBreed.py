from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class AnimalBreed(Base):
    __tablename__ = "animals_breeds"
    
    id: Mapped[int_primary_key]
    animal_breed: Mapped[str] = mapped_column(String(100), unique=True)
    animal_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("animals_types.id", ondelete="CASCADE"))
    animal_type = relationship("AnimalType", back_populates="breeds")

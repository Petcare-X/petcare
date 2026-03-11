from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class AnimalBreed(Base):
    __tablename__ = "animals_breeds"
    
    id: Mapped[int_primary_key]
    animal_breed_name: Mapped[int] = mapped_column(String(50), unique=True)
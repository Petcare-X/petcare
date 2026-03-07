from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class AnimalPedigree(Base):
    __tablename__ = "animals_pedigrees"
    
    id: Mapped[int_primary_key]
    animal_pedigree: Mapped[int] = mapped_column(String(50), unique=True)
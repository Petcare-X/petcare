from sqlalchemy import String, Text, Date, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import NUMERIC

from src.core.db import Base

from datetime import date
from typing import Annotated
from decimal import Decimal

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class PetInfo(Base):
    __tablename__ = "pets_info"

    id: Mapped[int_primary_key]
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    pet_date_of_birth: Mapped[date] = mapped_column(Date)
    pet_type: Mapped[int] = mapped_column(Integer, ForeignKey("animals_types.id", ondelete="CASCADE"))
    pet_breed: Mapped[int] = mapped_column(Integer, ForeignKey("animals_breeds.id", ondelete="CASCADE"))
    pet_pedigree: Mapped[int | None] = mapped_column(Integer, ForeignKey("animals_pedigrees.id", ondelete="CASCADE"), nullable=True)
    pet_neck_girth: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    pet_breast_girth: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    pet_length: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    pet_is_sterilized: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    pet_photo: Mapped[str] = mapped_column(Text)

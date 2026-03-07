from sqlalchemy import String, Text, Date, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base

from datetime import date
from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class PetInfo(Base):
    __tablename__ = "pets_info"
    
    id: Mapped[int_primary_key]
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    pet_date_of_birth: Mapped[date] = mapped_column(Date)
    pet_type: Mapped[int] = mapped_column(Integer, ForeignKey("animals_types.id", ondelete="CASCADE"))
    pet_breed: Mapped[int] = mapped_column(Integer, ForeignKey("animals_breeds.id", ondelete="CASCADE"))
    pet_pedigree: Mapped[int] = mapped_column(Integer, ForeignKey("animals_pedigrees.id", ondelete="CASCADE"))
    pet_neck_girth: Mapped[int] = mapped_column(Numeric)
    pet_breast_girth: Mapped[int] = mapped_column(Numeric)
    pet_lenght: Mapped[int] = mapped_column(Numeric)
    pet_is_sretylyzed: Mapped[bool | None] = mapped_column(Boolean)
    pet_photo: Mapped[str] = mapped_column(Text)

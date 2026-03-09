from sqlalchemy import Integer, Text, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class SmartDiet(Base):
    __tablename__ = "smart_diets"

    id: Mapped[int_primary_key]
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets_info.id", ondelete="CASCADE"))
    food_photo: Mapped[str | None] = mapped_column(Text, nullable=True)
    calculated_food_norm: Mapped[str | None] = mapped_column(String(50), nullable=True)

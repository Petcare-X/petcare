from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from sqlalchemy import (
    BIGINT,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class PetInfo(Base):
    __tablename__ = "pets_info"
    
    id: Mapped[int_primary_key]
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    pet_name: Mapped[str] = mapped_column(String(50))
    pet_date_of_birth: Mapped[date] = mapped_column(Date)
    animal_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("animals_types.id", ondelete="CASCADE"))
    animal_breed_id: Mapped[int] = mapped_column(Integer, ForeignKey("animals_breeds.id", ondelete="CASCADE"))
    pedigree: Mapped[bool] = mapped_column(Boolean)
    pet_neck_girth: Mapped[int] = mapped_column(Numeric)
    pet_breast_girth: Mapped[int] = mapped_column(Numeric)
    pet_length: Mapped[int] = mapped_column(Numeric)
    pet_is_sterylyzed: Mapped[bool | None] = mapped_column(Boolean)
    pet_weight: Mapped[Decimal] = mapped_column(Numeric)
    pet_photo_object_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    pet_photo_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pet_photo_size_bytes: Mapped[int | None] = mapped_column(BIGINT, nullable=True)
    pet_photo_etag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    pet_photo_uploaded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    shared_users = relationship("SharedUser", back_populates="pet", cascade="all, delete-orphan", lazy="dynamic")
    invites = relationship("PetInvite", back_populates="pet", cascade="all, delete-orphan", lazy="dynamic")

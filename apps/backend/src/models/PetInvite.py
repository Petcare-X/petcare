from sqlalchemy import ForeignKey, String, Integer, DateTime, Boolean, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

from typing import Annotated
from datetime import datetime

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class PetInvite(Base):
    __tablename__ = "pet_invite"

    id: Mapped[int_primary_key]
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets_info.id", ondelete="CASCADE"))
    created_by: Mapped[int] = mapped_column(ForeignKey("users_info.id"))
    invite_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uses_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    pet = relationship("PetInfo", back_populates="invites")

    __table_args__ = (
        Index("ix_pet_id_created_by", "pet_id", "created_by"),
    )

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)] 

class SharedUser(Base):
    __tablename__ = "shared_users"
    
    id: Mapped[int_primary_key]
    shared_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    shared_pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets_info.id", ondelete="CASCADE"))
    sharing_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sharing_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pet = relationship("PetInfo", back_populates="shared_users")

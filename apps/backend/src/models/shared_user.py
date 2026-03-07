from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)]

class SharedUser(Base):
    __tablename__ = "shared_users"
    
    id: Mapped[int_primary_key]
    shared_with_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets_info.id", ondelete="CASCADE"))
    shared_till: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    has_shared_pet: Mapped[bool | None] = mapped_column(Boolean)

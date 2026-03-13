from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

from typing import Annotated

int_primary_key = Annotated[int, mapped_column(primary_key=True)] 

'''
коммент от макса (по большей части для кира) - не сноси эту строчку и вставляй внутрь обычного id (который serial) её, 
это универсальная штука для того чтобы меньше писать одно и то же
'''

class SharedUser(Base):
    __tablename__ = "shared_users"
    
    id: Mapped[int_primary_key]
    shared_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users_info.id", ondelete="CASCADE"))
    shared_pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets_info.id", ondelete="CASCADE"))
    sharing_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sharing_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    pet = relationship("Pet", back_populates="shared_users")
